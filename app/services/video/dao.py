"""Abstract Video DAO - Base data access for all video content"""
import os
import logging
from typing import (Optional, Type)
from datetime import (datetime, timedelta)
from abc import ABC
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import db
from app.services.video.models import (
    Video,
    DownloadStatus
)
from app.core.errors.handlers import APIError

LOGGER: logging.Logger = logging.getLogger(__name__)

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
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("VideoDAO.create: DB error")
            raise APIError(500, "Database error")
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
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("VideoDAO.update: DB error")
            raise APIError(500, "Database error")
        return video
    
    def delete(self, video: Video) -> None:
        """
        Delete video from database
        Args:
            video: Video instance to delete
        """
        db.session.delete(video)
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("VideoDAO.delete: DB error")
            raise APIError(500, "Database error")
    
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
            if video.file_path and os.path.exists(video.file_path):
                try:
                    os.remove(video.file_path)
                except OSError as e:
                    LOGGER.warning(f"VideoDAO.cleanup_old_videos: could not delete file {video.file_path}: {e}")
            db.session.delete(video)
            count += 1
        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            LOGGER.exception("VideoDAO.cleanup_old_videos: DB error")
            raise APIError(500, "Database error")
        return count
