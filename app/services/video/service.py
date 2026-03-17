"""Abstract Video Service - Base business logic for video content"""
import logging
from flask import Response
from abc import ABC, abstractmethod
from typing import Optional
from app.services.video.models import (
    Video,
    ContentType,
    DownloadStatus,
)
from app.services.video.dao import VideoDAO
from app.services.streaming import StreamingService
from app.services.torrent import TorrentService, torrent_service as _torrent_service
from app.core.errors.handlers import APIError
from app.core.errors.messages import ERROR_MESSAGES

LOGGER = logging.getLogger(__name__)


class VideoService(ABC):
    """Abstract service providing common operations for video content"""

    def __init__(self, dao: VideoDAO):
        self.dao: VideoDAO = dao
        self.torrent_manager: TorrentService = _torrent_service
        self.streaming: StreamingService = StreamingService()
        LOGGER.info(f"{self.__class__.__name__}: initialized")
    
    @abstractmethod
    def get_content_type(self) -> ContentType:
        """Get content type for this service"""
        pass

    def create_from_external(self, external_data: dict) -> Video:
        """
        Create video from external provider data
        Args:
            external_data: Data from YTS, EZTV, etc.
        Returns:
            Created video instance
        """
        video_data: dict = {
            "title": external_data.get("title"),
            "year": external_data.get("year"),
            "rating": external_data.get("rating"),
            "genres": external_data.get("genres"),
            "synopsis": external_data.get("synopsis"),
            "thumbnail": external_data.get("thumbnail"),
            "large_cover": external_data.get("large_cover"),
            "provider": external_data.get("provider"),
            "external_id": str(external_data.get("id")),
            "tmdb_id": external_data.get("tmdb_id"),
            "torrents": external_data.get("torrents"),
            "content_type": self.get_content_type(),
        }
        return self.dao.create(**video_data)
    
    def get_by_id(self, video_id: int) -> Optional[Video]:
        """Get video by ID"""
        return self.dao.get_by_id(video_id)
    
    def get_by_id_as_dict(self, video_id: int) -> Optional[dict]:
        """Get video by ID as dictionary"""
        video: Optional[Video] = self.get_by_id(video_id)
        return video.to_dict() if video else None
    
    def get_by_torrent_hash(self, torrent_hash: str) -> Optional[Video]:
        """Get video by torrent hash"""
        return self.dao.get_by_torrent_hash(torrent_hash)
    
    def get_by_title(self, title: str) -> list[Video]:
        """Search videos by title"""
        return self.dao.get_by_title(title)
        
    def get_all(self) -> list[dict]:
        """Get all videos as dictionaries"""
        videos = self.dao.get_all()
        return [video.to_dict() for video in videos]

    def update_download_progress(
        self,
        video_id: int,
        progress: float,
        status: DownloadStatus = None
    ) -> Video:
        """
        Update download progress
        Args:
            video_id: Video ID
            progress: Progress percentage (0-100)
            status: Optional new download status
        Returns:
            Updated video
        """
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
        update_data: dict = {"download_progress": progress}
        if status:
            update_data["download_status"] = status
        return self.dao.update(video, **update_data)
    
    def complete_download(
        self,
        video_id: int,
        file_path: str
    ) -> Video:
        """
        Mark download as completed
        Args:
            video_id: Video ID
            file_path: Path to downloaded file
        Returns:
            Updated video
        """
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
        return self.dao.update(
            video,
            file_path=file_path,
            download_status=DownloadStatus.COMPLETED,
            download_progress=100.0
        )
    
    def update(self, video_id: int, data: dict) -> Optional[dict]:
        """Update a video"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            return None
        updated_video: Optional[Video] = self.dao.update(video, **data)
        return updated_video.to_dict() if updated_video else None
    
    def delete(self, video_id: int) -> bool:
        """Delete a video"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            LOGGER.warning(f"{self.__class__.__name__}: Delete: video_id={video_id} not found (already deleted?)")
            return False
        LOGGER.info(f"{self.__class__.__name__}: Deleting video: video_id={video_id} title='{video.title}'")
        self.dao.delete(video)
        return True
    
    def get_downloaded(self) -> list[Video]:
        """Get all downloaded videos"""
        return self.dao.get_downloaded()
    
    def get_statistics(self) -> dict:
        """Get statistics"""
        all_videos: list[Video] = self.dao.get_all()
        downloaded: list[Video] = self.dao.get_downloaded()
        downloading: list[Video] = [
            v for v in all_videos
                if v.download_status == DownloadStatus.DOWNLOADING
        ]
        return {
            "total": len(all_videos),
            "downloaded": len(downloaded),
            "downloading": len(downloading),
            "not_downloaded": len(all_videos) - len(downloaded) - len(downloading)
        }
    
    def start_download(self, data: dict) -> dict:
        """Start video download via Celery"""
        video_data: dict = {
            "title": data.get("title"),
            "year": data.get("year"),
            "rating": data.get("rating"),
            "genres": data.get("genres", []),
            "synopsis": data.get("synopsis"),
            "thumbnail": data.get("cover_image") or data.get("thumbnail"),
            "large_cover": data.get("cover_image"),
            "provider": "manual",
            "external_id": data.get("torrent_hash"),
            "torrents": [{"hash": data.get("torrent_hash"), "url": data.get("torrent_url")}],
            "selected_torrent_hash": data.get("torrent_hash"),
            "download_status": DownloadStatus.DOWNLOADING,
            "content_type": self.get_content_type(),
            "last_watched": None
        }
        video: Video = self.dao.create(**video_data)
        LOGGER.info(f"{self.__class__.__name__}: Starting download: content_type={self.get_content_type().value} title='{video.title}' hash={data.get('torrent_hash')} video_id={video.id}")

        from app.tasks.downloads import start_torrent_download

        try:
            task = start_torrent_download.delay(
                data.get("torrent_url"),
                data.get("torrent_hash"),
                video.id,
                self.get_content_type().value
            )
        except Exception as e:
            LOGGER.exception("%s: Failed to enqueue download task", self.__class__.__name__)
            self.dao.delete(video)
            raise APIError(503, ERROR_MESSAGES["SERVICE_UNAVAILABLE"])
        return {
            "message": "Download started",
            "video_id": video.id,
            "task_id": task.id,
            "video": video.to_dict()
        }
    
    def get_download_status(self, video_id: int) -> Optional[dict]:
        """Get download status"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video or not video.selected_torrent_hash:
            return None
        torrent_status: dict = self.torrent_manager.get_download_status(video.selected_torrent_hash)
        return {
            "video_id": video_id,
            "status": video.download_status.value if video.download_status else "unknown",
            "progress": video.download_progress or 0.0,
            "torrent_status": torrent_status
        }
    
    def pause_download(self, video_id: int) -> Optional[dict]:
        """Pause download"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video or not video.selected_torrent_hash:
            return None
        success: bool = self.torrent_manager.pause_download(video.selected_torrent_hash)
        LOGGER.debug("%s: pause_download video_id=%s %s", self.__class__.__name__, video_id, "ok" if success else "failed")
        if success:
            self.dao.update(video, download_status=DownloadStatus.PAUSED)
        return {"message": "Download paused" if success else "Failed to pause", "success": success}
    
    def resume_download(self, video_id: int) -> Optional[dict]:
        """Resume download"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            return None
        success: bool = self.torrent_manager.resume_download(video.selected_torrent_hash)
        if success:
            self.dao.update(video, download_status=DownloadStatus.DOWNLOADING)
        return {
            "message": "Download resumed" if success else "Failed to resume",
            "success": success,
        }
    
    def get_file_path_for_streaming(self, video_id: int) -> str:
        """
        Validate that a video is ready for streaming and return its absolute file path.
        Raises:
            APIError 404: video not found, not in a streamable state, or file path unresolvable.
        """
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
        streamable_statuses: tuple = (DownloadStatus.DOWNLOADING, DownloadStatus.COMPLETED)
        if video.download_status not in streamable_statuses:
            raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_STREAMABLE"])
        file_path: Optional[str] = video.file_path
        if not file_path and video.selected_torrent_hash:
            file_path = self.torrent_manager.get_video_file(video.selected_torrent_hash)
        if not file_path:
            raise APIError(404, ERROR_MESSAGES["VIDEO_FILE_NOT_FOUND"])
        return file_path

    def stream_video(
        self,
        video_id: int,
        range_header: Optional[str] = None
    ) -> Response:
        """
        Stream a video file via Flask (FFmpeg fallback for non-native formats).
        For native formats (mp4/webm/ogg), prefer the nginx X-Accel-Redirect path.
        Raises:
            APIError 404: video not found, not ready, or file missing.
            APIError 503: not enough data downloaded yet.
        """
        file_path: str = self.get_file_path_for_streaming(video_id)
        return self.streaming.stream(file_path, range_header)
