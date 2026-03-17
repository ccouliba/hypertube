"""Torrent domain — download manager and torrent service"""
from app.services.torrent.service import TorrentService

# Singleton — one authenticated session shared across VideoService and Celery tasks.
# Prevents multiple concurrent auth_log_in() calls that trigger qBittorrent IP bans.
torrent_service: TorrentService = TorrentService()

__all__ = [
    "TorrentService",
    "torrent_service",
]
