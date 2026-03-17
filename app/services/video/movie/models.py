"""Movies domain models"""
from app.services.video.models import (
    Video,
    ContentType
)


class Movie(Video):
    """Movie model - inherits from Video"""

    __tablename__ = "movie"

    __mapper_args__ = {
        "polymorphic_identity": ContentType.MOVIE,
    }
    
    def __repr__(self) -> None:
        return f"<Movie {self.title} ({self.year})>"
