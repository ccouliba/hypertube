import logging
from typing import Optional
from app.services.torrent import TorrentManager
from app.tasks import (
    celery_app,
    celery_settings as settings,
)

logging.basicConfig(level=logging.INFO)
LOGGER: logging.Logger = logging.getLogger(__name__)


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
        LOGGER.info(f"Starting torrent download for {content_type} video_id={video_id}")
        LOGGER.info(f"Torrent hash: {torrent_hash}")
        result: dict = TorrentManager.start_download(torrent_url, torrent_hash)
        LOGGER.info(f"Download started successfully for video_id: {video_id}")
        return {
            "status": "started",
            "torrent_url": torrent_url,
            "torrent_hash": torrent_hash,
            "video_id": video_id,
            "content_type": content_type,
            "result": result
        }
    except Exception as e:
        LOGGER.error(f"Error starting torrent download: {e}")
        self.retry(
            countdown=settings["RETRY_COUNTDOWN"],
            max_retries=settings["MAX_RETRIES"],
            exc=e
        )


@celery_app.task(name="tasks.monitor_torrent_status")
def monitor_torrent_status(torrent_hash: str) -> Optional[dict]:
    """
    Monitor the status of a torrent download
    Args:
        torrent_hash: The hash of the torrent to monitor
    Returns:
        Dict with current torrent status or None if not found
    """
    try:
        status: Optional[dict] = TorrentManager.get_download_status(torrent_hash)
        if status:
            LOGGER.info(f"Torrent {torrent_hash}: {status['progress']:.1f}% complete")
            if status["is_finished"]:
                LOGGER.info(f"Torrent {torrent_hash} download complete!")
        return status
    except Exception as e:
        LOGGER.error(f"Error monitoring torrent {torrent_hash}: {e}")
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
        success: bool = TorrentManager.remove_download(
            torrent_hash,
            delete_files
        )
        LOGGER.info(f"Torrent {torrent_hash} removed: {success}")
        return {
            "status": "removed" if success else "failed",
            "torrent_hash": torrent_hash
        }
    except Exception as e:
        LOGGER.error(f"Error removing torrent {torrent_hash}: {e}")
        return {"status": "error", "error": str(e)}


@celery_app.task(name="tasks.process_completed_download")
def process_completed_download(torrent_hash: str) -> dict:
    """
    Post-processing task after download completion
    Extracts video file, updates database, sends notifications, etc.
    Args:
        torrent_hash: The hash of the completed torrent
    Returns:
        Dict with processing results
    """
    try:
        video_file: Optional[str] = TorrentManager.get_video_file(torrent_hash)
        if video_file:
            LOGGER.info(f"Video file found: {video_file}")
            # Here I can:
            # - Update movie record in database with video path
            # - Send notification to user
            # - Start transcoding if needed
            return {
                "status": "processed",
                "video_file": video_file,
                "torrent_hash": torrent_hash
            }
        else:
            LOGGER.warning(f"No video file found for torrent {torrent_hash}")
            return {"status": "no_video_found", "torrent_hash": torrent_hash}
    except Exception as e:
        LOGGER.error(f"Error processing completed download {torrent_hash}: {e}")
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    # For testing purposes
    test_magnet: str = "magnet:?xt=urn:btih:EXAMPLEHASH&dn=Example"
    task = start_torrent_download.delay(test_magnet, movie_id=123)
    print(f"Started download task with ID: {task.id}")
