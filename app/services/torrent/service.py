"""
TorrentService - Wrapper for qBittorrent API
Manages torrent downloads, status tracking, and video file retrieval
"""
import os
from pathlib import Path
from typing import (Optional, Dict)
from qbittorrentapi import Client
from app.services.torrent.settings import qb_settings as settings
import logging

LOGGER = logging.getLogger(__name__)

HOST: str = settings["HOST"]
USERNAME: str = settings["USER"]
PASSWORD: str = settings["PASS"]
DOWNLOAD_DIR = settings["DOWNLOADS_DIR"]
Path(DOWNLOAD_DIR).mkdir(parents=True, exist_ok=True)
VIDEO_EXTENSIONS: set = set(settings["VIDEO_EXTENSIONS"])

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
        self.qb = Client(
            host=HOST,
            username=USERNAME,
            password=PASSWORD
        )
        LOGGER.info("TorrentService initialized with qBittorrent")
    
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
                save_path=DOWNLOAD_DIR
            )
            LOGGER.info(f"Started download - Hash: {torrent_hash}")
            return {
                "status": "started",
                "torrent_hash": torrent_hash,
                "save_path": DOWNLOAD_DIR
            }
        except Exception as e:
            LOGGER.error(f"Error starting download: {e}")
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
            torrents = self.qb.torrents_info(torrent_hashes=[torrent_hash])
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
            LOGGER.error(f"Error getting status for {torrent_hash}: {e}")
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
            LOGGER.info(f"Paused download for {torrent_hash}")
            return True
        except Exception as e:
            LOGGER.error(f"Error pausing {torrent_hash}: {e}")
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
            LOGGER.info(f"Resumed download for {torrent_hash}")
            return True
        except Exception as e:
            LOGGER.error(f"Error resuming {torrent_hash}: {e}")
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
            LOGGER.info(f"Removed torrent {torrent_hash} (delete_files={delete_files})")
            return True
        except Exception as e:
            LOGGER.error(f"Error removing {torrent_hash}: {e}")
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
            torrents = self.qb.torrents_info(torrent_hashes=[torrent_hash])
            if torrents:
                t = torrents[0]
                files = self.qb.torrents_files(torrent_hash=t.hash)
                # Find the largest video file
                video_extensions: set = VIDEO_EXTENSIONS
                largest_video = None
                largest_size = 0
                for file in files:
                    file_path = file.name
                    file_size = file.size
                    file_ext = Path(file_path).suffix.lower()                    
                    if file_ext in video_extensions and file_size > largest_size:
                        largest_video = os.path.join(t.save_path, file_path)
                        largest_size = file_size
                return largest_video
        except Exception as e:
            LOGGER.error(f"Error getting video file for {torrent_hash}: {e}")
        return None

TorrentManager: TorrentService = TorrentService()
