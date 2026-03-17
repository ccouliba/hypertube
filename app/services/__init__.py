"""Services package — all business logic entry points"""
from app.services.auth.service import AuthService
from app.services.video.service import VideoService
from app.services.streaming import StreamingService
from app.services.video.movie.service import MovieService
from app.services.video.tv_show.service import TVShowService
from app.services.search.service import SearchService
from app.services.torrent.service import TorrentService
from app.services.maintenance.service import MaintenanceService

__all__ = [
    "AuthService",
    "SearchService",
    "VideoService",
    "StreamingService",
    "MovieService",
    "TVShowService",
    "TorrentService",
    "MaintenanceService",
]
