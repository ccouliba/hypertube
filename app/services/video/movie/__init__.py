"""
Movies Sub-domain

Provides:
- Movie model inherits from Video (Movie)
- MovieDAO for database operations (MovieDAO)
- Singleton instance: Movie_Service (Movie_Service)
"""
from app.services.video.movie.models import Movie
from app.services.video.movie.dao import MovieDAO
from app.services.video.movie.service import MovieService

__all__ = [
    "Movie",
    "MovieDAO",
    "MovieService",
]
