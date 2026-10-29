import os
import logging
import subprocess
from pathlib import Path
from typing import Optional
from app.services.torrent import torrent_service
from app.services import MovieService, TVShowService
from app.services.video.models import DownloadStatus
from app.tasks.celery_app import celery_app
from app.core.configs import CELERY_CONFIG
from app.core.errors.handlers import APIError

logging.basicConfig(level=logging.INFO)
LOGGER: logging.Logger = logging.getLogger(__name__)

_retry = CELERY_CONFIG["retry"]
MONITOR_INTERVAL: int = int(os.getenv("TORRENT_MONITOR_INTERVAL", "5"))
MONITOR_MAX_ATTEMPTS: int = int(os.getenv("TORRENT_MONITOR_MAX_ATTEMPTS", "360"))
_ERROR_STATES: frozenset[str] = frozenset({"error", "missingfiles"})
_PAUSED_STATES: frozenset[str] = frozenset({"pausedl", "stoppeddl"})

# Extensions the browser plays natively
_BROWSER_NATIVE: frozenset = frozenset({".mp4", ".webm", ".ogg"})


def _update_progress(
    video_service: MovieService | TVShowService,
    video_id: int,
    progress: float,
    status: DownloadStatus | None = None,
) -> bool:
    """Update a task's video, returning False when the task is stale."""
    try:
        video_service.update_download_progress(video_id, progress, status)
        return True
    except APIError as exc:
        if exc.code == 404:
            LOGGER.warning(
                "Downloads: Ignoring stale task for missing video_id=%s",
                video_id,
            )
            return False
        raise


@celery_app.task(name="tasks.start_torrent_download", bind=True)
def start_torrent_download(
    self,
    torrent_url: str,
    torrent_hash: str,
    video_id: int,
    content_type: str
) -> dict:
    """
    Start downloading a torrent asynchronously via qBittorrent
    Args:
        torrent_url: The magnet link or torrent URL to download
        torrent_hash: The torrent hash
        video_id: Video ID (movie or TV show) to associate with the download
        content_type: Type of content ("movie" or "tv_show")
    Returns:
        Dict with download status and torrent info
    """    
    try:
        LOGGER.info(f"Downloads: Starting torrent download for {content_type} video_id={video_id}")
        LOGGER.info(f"Downloads: Torrent hash: {torrent_hash}")
        result: dict = torrent_service.start_download(torrent_url, torrent_hash)
        LOGGER.info(f"Downloads: Download started successfully for video_id: {video_id}")
        monitor_torrent_status.apply_async(
            args=[torrent_hash, video_id, content_type],
            countdown=MONITOR_INTERVAL
        )
        return {
            "status": "started",
            "torrent_url": torrent_url,
            "torrent_hash": torrent_hash,
            "video_id": video_id,
            "content_type": content_type,
            "result": result
        }
    except Exception as e:
        LOGGER.exception("Downloads: Error starting torrent download")
        self.retry(
            countdown=_retry["countdown"],
            max_retries=_retry["max_retries"],
            exc=e
        )


@celery_app.task(name="tasks.monitor_torrent_status")
def monitor_torrent_status(
    torrent_hash: str,
    video_id: int,
    content_type: str,
    attempt: int = 0,
) -> Optional[dict]:
    """
    Poll qBittorrent until the download finishes, then trigger post-processing.
    """
    try:
        status: Optional[dict] = torrent_service.get_download_status(torrent_hash)
        if status:
            LOGGER.info(f"Downloads: Torrent {torrent_hash}: {status['progress']:.1f}% — video_id={video_id}")
            video_service = MovieService() if content_type == "movie" else TVShowService()
            torrent_state = str(status.get("state", "")).lower()
            if torrent_state in _ERROR_STATES:
                _update_progress(
                    video_service,
                    video_id,
                    status["progress"],
                    DownloadStatus.ERROR,
                )
                LOGGER.error(
                    "Downloads: Torrent %s entered terminal error state: %s",
                    torrent_hash,
                    status["state"],
                )
                return status
            if torrent_state in _PAUSED_STATES:
                _update_progress(
                    video_service,
                    video_id,
                    status["progress"],
                    DownloadStatus.PAUSED,
                )
                LOGGER.info(
                    "Downloads: Torrent %s is paused/stopped: %s",
                    torrent_hash,
                    status["state"],
                )
                return status
            if not _update_progress(video_service, video_id, status["progress"]):
                return status
            if status["is_finished"]:
                LOGGER.info(f"Downloads: Torrent {torrent_hash} complete — triggering post-processing")
                process_completed_download.delay(torrent_hash, video_id, content_type)
                return status
        else:
            LOGGER.info(f"Downloads: Torrent {torrent_hash} not yet in qBittorrent, retrying in {MONITOR_INTERVAL}s")
        next_attempt = attempt + 1
        if next_attempt >= MONITOR_MAX_ATTEMPTS:
            video_service = MovieService() if content_type == "movie" else TVShowService()
            _update_progress(
                video_service,
                video_id,
                0.0,
                DownloadStatus.ERROR,
            )
            LOGGER.error(
                "Downloads: Monitoring timed out for torrent %s after %d attempts",
                torrent_hash,
                next_attempt,
            )
            return status
        monitor_torrent_status.apply_async(
            args=[torrent_hash, video_id, content_type, next_attempt],
            countdown=MONITOR_INTERVAL
        )
        return status
    except Exception as e:
        LOGGER.exception("Downloads: Error monitoring torrent %s", torrent_hash)
        return None


@celery_app.task(name="tasks.remove_torrent")
def remove_torrent(
    torrent_hash: str,
    delete_files: bool = False
) -> dict:
    """
    Remove a torrent from qBittorrent
    Args:
        torrent_hash: The hash of the torrent to remove
        delete_files: Whether to delete the downloaded files
    Returns:
        Dict with removal status
    """
    try:
        success: bool = torrent_service.remove_download(
            torrent_hash,
            delete_files
        )
        LOGGER.info(f"Downloads: Torrent {torrent_hash} removed: {success}")
        return {
            "status": "removed" if success else "failed",
            "torrent_hash": torrent_hash
        }
    except Exception as e:
        LOGGER.exception("Downloads: Error removing torrent %s", torrent_hash)
        return {"status": "error", "error": str(e)}


@celery_app.task(name="tasks.process_completed_download")
def process_completed_download(
    torrent_hash: str,
    video_id: int,
    content_type: str
) -> dict:
    """
    Post-processing after a torrent finishes:
    - Resolves the video file on disk
    - Marks the video COMPLETED in DB and persists file_path
    - Triggers convert_video if the container is not browser-native (MKV, AVI…)
    """
    try:
        video_file: Optional[str] = torrent_service.get_video_file(torrent_hash)
        if not video_file:
            LOGGER.warning(f"Downloads: No video file found for torrent {torrent_hash}")
            return {"status": "no_video_found", "torrent_hash": torrent_hash}
        video_service = MovieService() if content_type == "movie" else TVShowService()
        try:
            video_service.complete_download(video_id, video_file)
            LOGGER.info(f"Downloads: video_id={video_id} marked COMPLETED — file: {video_file}")
        except (ValueError, APIError):
            LOGGER.warning(f"Downloads: video_id={video_id} not found in DB")
        ext: str = Path(video_file).suffix.lower() # Schedule FFmpeg remux for non-native containers (one-time, async)
        if ext not in _BROWSER_NATIVE:
            LOGGER.info(f"Downloads: Non-native container {ext} — scheduling conversion for video_id={video_id}")
            convert_video.delay(video_id, content_type, video_file)
        return {
            "status": "processed",
            "video_id": video_id,
            "video_file": video_file,
            "torrent_hash": torrent_hash,
        }
    except Exception as e:
        LOGGER.exception("Downloads: Error processing completed download %s", torrent_hash)
        return {"status": "error", "error": str(e)}


@celery_app.task(name="tasks.convert_video")
def convert_video(
    video_id: int,
    content_type: str,
    input_path: str
) -> dict:
    """
    Remux a non-native container (MKV, AVI…) to MP4 using FFmpeg -c copy.
    No re-encoding: fast and lossless.
    Updates file_path in DB so subsequent streams use direct Range requests.
    """
    output_path: str = str(Path(input_path).with_suffix(".mp4"))
    if input_path == output_path:
        LOGGER.info(f"Downloads: Already .mp4, skipping conversion: {input_path}")
        return {"status": "skipped", "file": input_path}
    try:
        LOGGER.info(f"Downloads: Converting {input_path} → {output_path} for video_id={video_id}")
        proc: subprocess.CompletedProcess = subprocess.run(
            [
                "ffmpeg", "-i", input_path,
                "-c", "copy",
                "-movflags", "faststart",
                "-y", output_path,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        if proc.returncode != 0:
            error = proc.stderr.decode(errors="replace")
            LOGGER.error(f"Downloads: FFmpeg failed for video_id={video_id}: {error}")
            return {"status": "error", "error": error}
        video_service = MovieService() if content_type == "movie" else TVShowService()
        video_service.update(video_id, {"file_path": output_path})
        LOGGER.info(f"Downloads: video_id={video_id} file_path updated to {output_path}")
        try:
            os.remove(input_path) # Remove original non-native file to save disk space
        except OSError as e:
            LOGGER.warning(f"Downloads: Could not delete original file {input_path}: {e}")
        return {"status": "converted", "output": output_path}
    except Exception as e:
        LOGGER.exception("Downloads: Error converting video_id=%s", video_id)
        return {"status": "error", "error": str(e)}
