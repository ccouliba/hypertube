"""Movie DAO - Data Access Object for movies"""
from app.services.video.dao import VideoDAO
from app.services.video.movie.models import Movie


class MovieDAO(VideoDAO):
    """DAO for Movie model - inherits common video operations"""
    
    def __init__(self) -> None:
        super().__init__(Movie)
