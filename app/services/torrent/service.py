"""
TorrentService - Wrapper for qBittorrent API
Manages torrent downloads, status tracking, and video file retrieval
"""
import os
from pathlib import Path
from typing import (Optional, Dict)
from qbittorrentapi import Client
from app.core.configs import QBT_CONFIG
import logging
import time

LOGGER: logging.Logger = logging.getLogger(__name__)

HOST: str = QBT_CONFIG["qbittorrent"]["host"]
USERNAME: str = QBT_CONFIG["qbittorrent"]["user"]
PASSWORD: str = QBT_CONFIG["qbittorrent"]["pass"]
DOWNLOAD_DIR: str = QBT_CONFIG["downloads"]["directory"]
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
VIDEO_EXTENSIONS: set = set(QBT_CONFIG["video"]["extensions"])


class TorrentService:
    """
    Manages torrent downloads using qBittorrent API
    This service provides:
    - Starting/pausing/resuming downloads
    - Status tracking and progress monitoring
    - Video file detection and retrieval
    - Torrent removal with optional file deletion
    """

    def __init__(self) -> None:
        """Initialize qBittorrent client with credentials from config"""
        self.qb: Client = Client(
            host=HOST,
            REQUESTS_ARGS={"timeout": 10},
        )
        try:
            self.qb.app_version()  # Test connection
            LOGGER.info("TorrentService: initialized and connected to qBittorrent")
        except Exception as e:
            LOGGER.warning(f"TorrentService: initial connection failed: {e}")
    
    def start_download(
        self,
        torrent_url: str,
        torrent_hash: str = None
    ) -> Dict:
        """
        Start downloading a torrent via qBittorrent API
        Args:
            torrent_url: Magnet link or torrent URL
            torrent_hash: Optional torrent hash (for tracking)
        Returns:
            Dict with status and download info
        Raises:
            Exception: If download fails to start
        """
        try:
            self.qb.torrents_add(
                urls=torrent_url,
                save_path=DOWNLOAD_DIR,
                is_sequential_download=True,
                is_first_last_piece_priority=True
            )
            LOGGER.info(f"TorrentService: Started download — hash: {torrent_hash}")
            return {
                "status": "started",
                "torrent_hash": torrent_hash,
                "save_path": DOWNLOAD_DIR
            }
        except Exception as e:
            LOGGER.exception("TorrentService: Error starting download")
            raise
    
    def get_download_status(
        self,
        torrent_hash: str
    ) -> Optional[Dict]:
        """
        Get detailed status of a torrent download
        Args:
            torrent_hash: Hash of the torrent
        Returns:
            Dict with progress, speeds, peers, etc. or None if not found
        """
        try:
            torrents: list = self.qb.torrents_info(torrent_hashes=[torrent_hash])
            if torrents:
                t = torrents[0]
                return {
                    "torrent_hash": torrent_hash,
                    "name": t.name,
                    "progress": t.progress * 100,
                    "download_rate": t.dlspeed,
                    "upload_rate": t.upspeed,
                    "num_peers": t.num_leechs,
                    "num_seeds": t.num_seeds,
                    "state": t.state,
                    "save_path": t.save_path,
                    "total_done": t.downloaded,
                    "total_wanted": t.size,
                    "is_finished": t.progress == 1.0,
                    "is_seeding": t.state == "uploading",
                }
        except Exception as e:
            LOGGER.exception("TorrentService: Error getting status for %s", torrent_hash)
        return None
    
    def pause_download(self, torrent_hash: str) -> bool:
        """
        Pause a torrent download
        Args:
            torrent_hash: Hash of the torrent to pause
        Returns:
            True if successful, False otherwise
        """
        try:
            self.qb.torrents_pause(torrent_hashes=[torrent_hash])
            LOGGER.info(f"TorrentService: Paused download for {torrent_hash}")
            return True
        except Exception as e:
            LOGGER.exception("TorrentService: Error pausing %s", torrent_hash)
            return False
    
    def resume_download(self, torrent_hash: str) -> bool:
        """
        Resume a paused torrent download
        Args:
            torrent_hash: Hash of the torrent to resume
        Returns:
            True if successful, False otherwise
        """
        try:
            self.qb.torrents_resume(torrent_hashes=[torrent_hash])
            LOGGER.info(f"TorrentService: Resumed download for {torrent_hash}")
            return True
        except Exception as e:
            LOGGER.exception("TorrentService: Error resuming %s", torrent_hash)
            return False
    
    def remove_download(
            self,
            torrent_hash: str,
            delete_files: bool = False
        ) -> bool:
        """
        Remove a torrent from qBittorrent
        Args:
            torrent_hash: Hash of the torrent to remove
            delete_files: Whether to delete downloaded files
        Returns:
            True if successful, False otherwise
        """
        try:
            self.qb.torrents_delete(torrent_hashes=[torrent_hash], delete_files=True)
            LOGGER.info(f"TorrentService: Removed torrent {torrent_hash} (delete_files={delete_files})")
            return True
        except Exception as e:
            LOGGER.exception("TorrentService: Error removing %s", torrent_hash)
            return False
    
    def get_video_file(self, torrent_hash: str) -> Optional[str]:
        """
        Get the path to the main video file in a torrent
        Finds the largest video file by extension
        Args:
            torrent_hash: Hash of the torrent
        Returns:
            Full path to the video file or None if not found
        """
        try:
            torrents: list = self.qb.torrents_info(torrent_hashes=[torrent_hash])
            if torrents:
                t = torrents[0]
                files: list = self.qb.torrents_files(torrent_hash=t.hash)
                # Find the largest video file
                video_extensions: set = VIDEO_EXTENSIONS
                largest_video: str | None = None
                largest_size: int = 0
                for file in files:
                    file_path = file.name
                    file_size = file.size
                    file_ext: str = Path(file_path).suffix.lower()                    
                    if file_ext in video_extensions and file_size > largest_size:
                        largest_video: str | None = os.path.join(t.save_path, file_path)
                        largest_size: int = file_size
                return largest_video
        except Exception as e:
            LOGGER.error(f"TorrentService: Error getting video file for {torrent_hash}: {e}")
        return None
