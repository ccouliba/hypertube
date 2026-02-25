"""Settings for the torrent service.
Provides configuration constants for connecting to the qBittorrent client
and managing torrent downloads.
"""
from app.core.configs.qbittorrent import QBT_CONFIG as qb_conf

qb_settings: dict = {
    "HOST": str(qb_conf["qbittorrent"]["host"]),
    "USER": str(qb_conf["qbittorrent"]["user"]),
    "PASS": str(qb_conf["qbittorrent"]["pass"]),
    "DOWNLOADS_DIR": str(qb_conf["downloads"]["directory"]),
    "VIDEO_EXTENSIONS": set(qb_conf["video"]["extensions"]),
}
