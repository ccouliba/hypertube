"""Torrent services package initialization

Provides:
- Torrent download manager
- Torrent Service for business logic
- Singleton instance: TorrentManager
"""
from app.services.torrent.service import TorrentManager

__all__ = [
    "TorrentManager",
]
