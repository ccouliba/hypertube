"""TV Show DAO - Data Access Object for TV shows"""
from app.services.video.dao import VideoDAO
from app.services.video.tv_show.models import TVShow


class TVShowDAO(VideoDAO):
    """DAO for TVShow model - inherits common video operations"""
    
    def __init__(self):
        super().__init__(TVShow)
