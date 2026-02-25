"""
Domain services module - Business logic and service layers

This module provides:
- Models for each service
- Authentication service
- Video management service
- Torrent handling service
"""
from app.services.auth.service import AuthService
from app.services.video.service import VideoService
from app.services.video.movie.service import MovieService
from app.services.video.tv_show.service import TVShowService
from app.services.search.service import SearchService
from app.services.torrent.service import TorrentService

__all__ = [
    "AuthService",
    "SearchService",
    "VideoService",
    "MovieService",
    "TVShowService",
    "TorrentService",
]
