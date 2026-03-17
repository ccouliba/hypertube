"""TV Show Service - inherits from VideoService"""
from app.services.video.models import ContentType
from app.services.video.service import VideoService
from app.services.video.tv_show import TVShowDAO


class TVShowService(VideoService):
    """Service for TV show operations"""
    
    def __init__(self) -> None:
        super().__init__(TVShowDAO())
    
    def get_content_type(self) -> ContentType:
        return ContentType.TV_SHOW
