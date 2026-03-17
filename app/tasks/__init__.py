"""Tasks package — Celery app, async downloads and maintenance tasks"""
from app.tasks.celery_app import celery_app
from app.tasks.downloads import (
    start_torrent_download,
    monitor_torrent_status,
    remove_torrent,
    process_completed_download,
)
from app.tasks.maintenance import cleanup_old_videos

__all__ = [
    "celery_app",
    "start_torrent_download",
    "monitor_torrent_status",
    "remove_torrent",
    "process_completed_download",
    "cleanup_old_videos",
]
