"""QBittorrent service configurations"""
import os

QBT_CONFIG: dict[str, any] = {
    "qbittorrent": {
        "host": os.getenv("QBITTORRENT_HOST", "http://qbittorrent:8080"),
        "user": os.getenv("QBITTORRENT_USER", "admin"),
        "pass": os.getenv("QBITTORRENT_PASSWORD", "secret123"),
        "timeout": int(os.getenv("QB_TIMEOUT", "30")),
    },
    "downloads": {
        "directory": os.getenv("DOWNLOAD_DIR", "/downloads"),
        "max_concurrent": int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5")),
    },
    "video": {
        "extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "min_size_mb": int(os.getenv("MIN_VIDEO_SIZE_MB", "100")),
    }
}
