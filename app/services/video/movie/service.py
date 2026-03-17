"""Movie Service - inherits from VideoService"""
from app.services.video.service import VideoService
from app.services.video.models import ContentType
from app.services.video.movie.dao import MovieDAO


class MovieService(VideoService):
    """Service for movie operations"""
    
    def __init__(self) -> None:
        super().__init__(MovieDAO())
    
    def get_content_type(self) -> ContentType:
        return ContentType.MOVIE
