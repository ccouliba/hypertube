"""TV Shows domain models"""
from app.services.video.models import (
    Video,
    ContentType
)

class TVShow(Video):
    """TV Show model - inherits from Video"""

    __tablename__ = "tv_show"
    __mapper_args__ = {
        "polymorphic_identity": ContentType.TV_SHOW.value,
    }

    def __repr__(self) -> str:
        return f"<TVShow {self.title} ({self.year})>"
