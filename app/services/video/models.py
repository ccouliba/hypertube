"""Abstract Video model - Base for all video content"""
import enum
from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    JSON,
    Enum as SQLEnum
)
from sqlalchemy.ext.declarative import declared_attr
from app.db.session import db


class ContentType(enum.Enum):
    """Content type enumeration"""
    MOVIE: str = "movie"
    TV_SHOW: str = "tv_show"


class DownloadStatus(enum.Enum):
    """Download status enumeration"""
    NOT_DOWNLOADED: str = "not_downloaded"
    DOWNLOADING: str = "downloading"
    COMPLETED: str = "completed"
    PAUSED: str = "paused"
    ERROR: str = "error"


class Video(db.Model):
    """Abstract base class for all video content"""

    __abstract__: bool = True
    __allow_unmapped__: bool = True
    
    id = Column(Integer, primary_key=True)
    content_type = Column(SQLEnum(ContentType), nullable=False)
    title = Column(String(255), nullable=False, index=True)
    year = Column(Integer, nullable=True)
    rating = Column(Float, nullable=True)
    genres = Column(JSON, nullable=True)
    synopsis = Column(String(2000), nullable=True)
    thumbnail = Column(String(500), nullable=True)
    large_cover = Column(String(500), nullable=True)
    provider = Column(String(50), nullable=True)
    external_id = Column(String(100), nullable=True)
    tmdb_id = Column(Integer, nullable=True)
    torrents = Column(JSON, nullable=True)
    selected_torrent_hash = Column(
        String(40),
        nullable=True,
        index=True
    )
    download_status = Column(
        SQLEnum(DownloadStatus),
        default=DownloadStatus.NOT_DOWNLOADED,
        nullable=False
    )
    download_progress = Column(Float, default=0.0)
    file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_watched = Column(DateTime, nullable=True)

    @declared_attr
    def __mapper_args__(cls: "Video") -> dict:
        """Configure polymorphic mapping"""
        if cls.__name__ == "Video":
            return {
                "polymorphic_identity": "video",
                "polymorphic_on": cls.content_type
            }
        return {}
    
    def to_dict(self) -> dict:
        """Convert to dictionary for API responses"""
        return {
            "id": self.id,
            "title": self.title,
            "year": self.year,
            "rating": self.rating,
            "genres": self.genres,
            "synopsis": self.synopsis,
            "thumbnail": self.thumbnail,
            "large_cover": self.large_cover,
            "provider": self.provider,
            "external_id": self.external_id,
            "tmdb_id": self.tmdb_id,
            "torrents": self.torrents,
            "download_status": self.download_status.value
                if self.download_status
                else "not_downloaded",
            "download_progress": self.download_progress,
            "file_path": self.file_path,
            "content_type": self.content_type.value
                if self.content_type
                else None,
            "created_at": self.created_at.isoformat()
                if self.created_at
                else None,
            "last_watched": self.last_watched.isoformat()
                if self.last_watched
                else None,
        }
