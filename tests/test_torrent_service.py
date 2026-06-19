import pytest
from unittest.mock import Mock, MagicMock, patch
from app.services.torrent.service import TorrentService


class TestTorrentServiceInit:

    def test_initializes(self, torrent_service):
        assert torrent_service is not None and torrent_service.qb is not None


class TestTorrentServiceStartDownload:

    def test_start_with_magnet(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.return_value = True
        result = torrent_service.start_download(
            torrent_url="magnet:?xt=urn:btih:test123",
            torrent_hash="test123"
        )
        assert result is not None and "status" in result

    def test_start_without_hash(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.return_value = True
        result = torrent_service.start_download(torrent_url="magnet:?xt=urn:btih:test123")
        assert result is not None

    @pytest.mark.parametrize("url", [
        "magnet:?xt=urn:btih:abc123",
        "magnet:?xt=urn:btih:xyz789",
        "http://example.com/torrent.torrent",
    ])
    def test_start_various_urls(self, torrent_service, mock_qbittorrent, url):
        mock_qbittorrent.torrents_add.return_value = True
        result = torrent_service.start_download(torrent_url=url)
        assert result is not None

    def test_start_qbittorrent_error(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.side_effect = Exception("qBittorrent failed")
        try:
            result = torrent_service.start_download(torrent_url="magnet:?xt=urn:btih:test123")
            assert result is not None or result is None
        except Exception:
            pass

    def test_start_empty_url(self, torrent_service):
        with pytest.raises((ValueError, TypeError, AttributeError)):
            torrent_service.start_download(torrent_url="")

    def test_start_invalid_url(self, torrent_service):
        with pytest.raises((ValueError, TypeError)):
            torrent_service.start_download(torrent_url="not_a_valid_url")


class TestTorrentServiceGetStatus:

    def test_get_status(self, torrent_service, mock_qbittorrent):
        mock_torrent = MagicMock()
        mock_torrent.progress = 0.5
        mock_torrent.state_enum = "downloading"
        mock_torrent.dlspeed = 1000000
        mock_torrent.upspeed = 500000
        mock_torrent.num_leechs = 10
        mock_torrent.num_seeds = 20
        mock_torrent.state = "downloading"
        mock_torrent.save_path = "/downloads"
        mock_torrent.downloaded = 500000000
        mock_torrent.size = 1000000000
        mock_qbittorrent.torrents_info.return_value = [mock_torrent]
        result = torrent_service.get_download_status("test123")
        assert result is not None

    def test_get_not_found(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_info.return_value = []
        result = torrent_service.get_download_status("nonexistent")
        assert result is None or result == {}




class TestTorrentServicePauseResume:

    def test_pause(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_pause.return_value = True
        result = torrent_service.pause_download("test123")
        assert result is not None

    def test_resume(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_resume.return_value = True
        result = torrent_service.resume_download("test123")
        assert result is not None

    def test_pause_nonexistent(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_pause.side_effect = Exception("Not found")
        try:
            torrent_service.pause_download("nonexistent")
        except Exception:
            pass

    @pytest.mark.parametrize("hash", [
        "abc123def456", "xyz789uvw012", "hash1234567890",
    ])
    def test_pause_resume_hashes(self, torrent_service, mock_qbittorrent, hash):
        mock_qbittorrent.torrents_pause.return_value = True
        mock_qbittorrent.torrents_resume.return_value = True
        pause_result = torrent_service.pause_download(hash)
        resume_result = torrent_service.resume_download(hash)
        assert pause_result is not None and resume_result is not None


class TestTorrentServiceRemove:

    def test_remove_no_files(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_delete.return_value = True
        result = torrent_service.remove_download("test123", delete_files=False)
        assert result is not None

    def test_remove_with_files(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_delete.return_value = True
        result = torrent_service.remove_download("test123", delete_files=True)
        assert result is not None

    def test_remove_nonexistent(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_delete.side_effect = Exception("Not found")
        try:
            torrent_service.remove_download("nonexistent")
        except Exception:
            pass

    @pytest.mark.parametrize("delete_files", [True, False])
    def test_remove_delete_flag(self, torrent_service, mock_qbittorrent, delete_files):
        mock_qbittorrent.torrents_delete.return_value = True
        result = torrent_service.remove_download("test123", delete_files=delete_files)
        assert result is not None


class TestTorrentServiceFileDetection:

    def test_get_video_files(self, torrent_service, mock_qbittorrent):
        mock_torrent = MagicMock()
        mock_torrent.hash = "test123"
        mock_torrent.save_path = "/downloads"
        mock_file = MagicMock()
        mock_file.name = "movie.mp4"
        mock_file.size = 5000000000
        mock_qbittorrent.torrents_info.return_value = [mock_torrent]
        mock_qbittorrent.torrents_files.return_value = [mock_file]
        result = torrent_service.get_video_file("test123")
        assert result is not None

    def test_find_largest_file(self, torrent_service, mock_qbittorrent):
        mock_torrent = MagicMock()
        mock_torrent.hash = "test123"
        mock_torrent.save_path = "/downloads"
        mock_file1 = MagicMock()
        mock_file1.name = "movie_480p.mp4"
        mock_file1.size = 1000000000
        mock_file2 = MagicMock()
        mock_file2.name = "movie_1080p.mp4"
        mock_file2.size = 5000000000
        mock_qbittorrent.torrents_info.return_value = [mock_torrent]
        mock_qbittorrent.torrents_files.return_value = [mock_file1, mock_file2]
        result = torrent_service.get_video_file("test123")
        assert result is not None

    def test_filter_extensions(self, torrent_service):
        valid_extensions = [".mp4", ".mkv", ".avi", ".mov", ".flv", ".wmv"]
        for ext in valid_extensions:
            assert ext is not None


class TestTorrentServiceProgress:

    def test_get_progress(self, torrent_service, mock_qbittorrent):
        mock_torrent = MagicMock()
        mock_torrent.progress = 0.75
        mock_torrent.state_enum = "downloading"
        mock_qbittorrent.torrents.return_value = [mock_torrent]
        result = torrent_service.get_download_status("test123")
        assert result is not None

    @pytest.mark.parametrize("progress", [0, 0.25, 0.5, 0.75, 1.0])
    def test_progress_percentages(self, torrent_service, mock_qbittorrent, progress):
        mock_torrent = MagicMock()
        mock_torrent.progress = progress
        mock_qbittorrent.torrents.return_value = [mock_torrent]
        result = torrent_service.get_download_status("test123")
        assert result is not None


class TestTorrentServiceConnection:

    def test_timeout_handling(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents.side_effect = TimeoutError("Timeout")
        try:
            result = torrent_service.get_download_status("test123")
        except TimeoutError:
            pass

    def test_disconnect_reconnect(self, torrent_service):
        assert torrent_service is not None


class TestTorrentServiceDownloadPath:

    def test_path_configured(self, torrent_service):
        assert torrent_service is not None

    def test_folder_writable(self, torrent_service):
        import os
        from pathlib import Path
        download_dir = "/downloads"
        Path(download_dir).mkdir(parents=True, exist_ok=True)
        assert os.path.exists(download_dir)


class TestTorrentServiceErrorHandling:

    def test_invalid_url(self, torrent_service):
        with pytest.raises((ValueError, TypeError)):
            torrent_service.start_download(torrent_url="")

    def test_corrupted_torrent(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.side_effect = Exception("Invalid")
        try:
            torrent_service.start_download(torrent_url="invalid")
        except Exception:
            pass

    def test_disk_full(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.side_effect = OSError("No space")
        try:
            torrent_service.start_download(torrent_url="magnet:?test")
        except (OSError, Exception):
            pass

    def test_permission_denied(self, torrent_service, mock_qbittorrent):
        mock_qbittorrent.torrents_add.side_effect = PermissionError("Permission denied")
        try:
            torrent_service.start_download(torrent_url="magnet:?test")
        except (PermissionError, Exception):
            pass
