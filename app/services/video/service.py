"""Abstract Video Service - Base business logic for video content"""
import os
from flask import (Response, send_file)
from abc import ABC, abstractmethod
from typing import Optional
from app.services.video.models import (
    Video,
    ContentType,
    DownloadStatus,
)
from app.services.video.dao import VideoDAO
from app.services.torrent.service import TorrentManager
from app.tasks.downloads import start_torrent_download


class VideoService(ABC):
    """Abstract service providing common operations for video content"""

    def __init__(self, dao: VideoDAO):
        self.dao = dao
        self.torrent_manager = TorrentManager
    
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
        video = self.dao.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        update_data = {"download_progress": progress}
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
        video = self.dao.get_by_id(video_id)
        if not video:
            raise ValueError(f"Video {video_id} not found")
        return self.dao.update(
            video,
            file_path=file_path,
            download_status=DownloadStatus.COMPLETED,
            download_progress=100.0
        )
    
    def update(self, video_id: int, data: dict) -> Optional[dict]:
        """Update a video"""
        video = self.dao.get_by_id(video_id)
        if not video:
            return None
        updated_video = self.dao.update(video, **data)
        return updated_video.to_dict() if updated_video else None
    
    def delete(self, video_id: int) -> bool:
        """Delete a video"""
        video = self.dao.get_by_id(video_id)
        if not video:
            return False
        return self.dao.delete(video)
    
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
        print(f"Creating video for download: {video_data['title']} - {video_data['download_status']}")
        video: Video = self.dao.create(**video_data)
        task = start_torrent_download.delay(
            data.get("torrent_url"),
            data.get("torrent_hash"),
            video.id,
            self.get_content_type().value
        )
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
        print(f"Pausing download for video ID {video_id}: {'success' if success else 'failed'}")
        if success:
            self.dao.update(video, download_status=DownloadStatus.PAUSED)
        return {"message": "Download paused" if success else "Failed to pause", "success": success}
    
    def resume_download(self, video_id: int) -> Optional[dict]:
        """Resume download"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video:
            return None
        success = self.torrent_manager.resume_download(video.selected_torrent_hash)
        if success:
            self.dao.update(video, download_status=DownloadStatus.DOWNLOADING)
        return {
            "message": "Download resumed"
                if success 
                    else "Failed to resume", "success": success
        }
    
    def stream_video(self, video_id: int) -> Optional[Response]:
        """Stream a downloaded video"""
        video: Optional[Video] = self.dao.get_by_id(video_id)
        if not video or video.download_status != DownloadStatus.COMPLETED or not video.file_path:
            return None
        if not os.path.exists(video.file_path):
            return None
        return send_file(
            video.file_path,
            mimetype="video/mp4",
            as_attachment=False,
            download_name=f"{video.title}.mp4"
        )
