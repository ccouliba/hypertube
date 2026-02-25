"""Abstract Video DAO - Base data access for all video content"""
import os
from typing import (Optional, Type)
from datetime import (datetime, timedelta)
from abc import ABC
from app.db.session import db
from app.services.video.models import (
    Video,
    DownloadStatus
)


class VideoDAO(ABC):
    """Abstract DAO providing common operations for video content"""
    
    def __init__(self, model_class: Type[Video]):
        """
        Initialize DAO with specific video model class
        Args:
            model_class: Movie or TVShow model class
        """
        self.model_class: Type[Video] = model_class
            
    def create(self, **kwargs) -> Video:
        """
        Create new video
        Args:
            **kwargs: Video attributes
        Returns:
            Created video instance
        """
        video: Video = self.model_class(**kwargs)
        db.session.add(video)
        db.session.commit()
        return video

    def get_by_id(self, video_id: int) -> Optional[Video]:
        """Get video by ID"""
        return self.model_class.query.filter_by(id=video_id).first()
    
    def get_by_torrent_hash(self, torrent_hash: str) -> Optional[Video]:
        """Get video by torrent hash"""
        return self.model_class.query.filter_by(
            selected_torrent_hash=torrent_hash
        ).first()
    
    def get_by_title(self, title: str) -> list[Video]:
        """Get videos by title (case-insensitive partial match)"""
        return self.model_class.query.filter(
            self.model_class.title.ilike(f"%{title}%")
        ).all()
    
    def get_all(self) -> list[Video]:
        """Get all videos of this type"""
        return self.model_class.query.all()
    
    def update(self, video: Video, **kwargs) -> Video:
        """
        Update video attributes
        Args:
            video: Video instance to update
            **kwargs: Attributes to update
        Returns:
            Updated video instance
        """
        for key, value in kwargs.items():
            if hasattr(video, key):
                setattr(video, key, value)
        db.session.commit()
        return video
    
    def delete(self, video: Video) -> None:
        """
        Delete video from database
        Args:
            video: Video instance to delete
        """
        db.session.delete(video)
        db.session.commit()
    
    def get_downloaded(self) -> list[Video]:
        """Get all completed downloads"""
        return self.model_class.query.filter(
            self.model_class.download_status== DownloadStatus.COMPLETED
        ).all()
    
    def get_downloading(self) -> list[Video]:
        """Get all currently downloading videos"""
        return self.model_class.query.filter(
            self.model_class.download_status == DownloadStatus.DOWNLOADING
        ).all()
    
    def cleanup_old_videos(self, days: int = 30) -> int:
        """Delete videos not watched for specified days and their files"""        
        cutoff_date: datetime = datetime.utcnow() - timedelta(days=days)
        old_videos: list[Video] = self.model_class.query.filter(
            db.or_(
                self.model_class.last_watched.is_(None),
                self.model_class.last_watched < cutoff_date
            )
        ).all()
        count: int = 0
        for video in old_videos:
            # Delete file from disk if exists
            if video.file_path and os.path.exists(video.file_path):
                try:
                    os.remove(video.file_path)
                except Exception as e:
                    print(f"Error deleting file {video.file_path}: {e}")
            db.session.delete(video)
            count += 1
        db.session.commit()
        return count
