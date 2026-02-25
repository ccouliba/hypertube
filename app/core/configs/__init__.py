"""Configuration module - Centralized app configuration

Provides:
    - Auth and App-level configuration
    - Database configuration
    - Celery/Redis configuration
    - qBittorrent configuration
    - Search providers configuration (Torrent)
    - Environment-specific settings
"""
from app.core.configs.general import G_CONFIG as APP_CONFIG
from app.core.configs.sqlalchemy import DB_CONFIG
from app.core.configs.auth import AUTH_CONFIG
from app.core.configs.celery import CELERY_CONFIG
from app.core.configs.qbittorrent import QBT_CONFIG
from app.core.configs.providers import PROVIDERS_CONFIG

__all__ = [
    "APP_CONFIG",
    "DB_CONFIG",
    "PROVIDERS_CONFIG",
    "CELERY_CONFIG",
    "QBT_CONFIG",
    "AUTH_CONFIG",
]
