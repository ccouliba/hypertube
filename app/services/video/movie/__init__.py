"""Movie sub-domain — model, DAO and service"""
from app.services.video.movie.models import Movie
from app.services.video.movie.dao import MovieDAO
from app.services.video.movie.service import MovieService

__all__ = [
    "Movie",
    "MovieDAO",
    "MovieService",
]
