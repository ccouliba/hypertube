"""Configuration module — all settings are defined in config.py."""
from app.core.configs.config import (
    APP_CONFIG,
    DB_CONFIG,
    AUTH_CONFIG,
    CELERY_CONFIG,
    REDIS_CONFIG,
    QBT_CONFIG,
    PROVIDERS_CONFIG,
)

__all__ = [
    "APP_CONFIG",
    "DB_CONFIG",
    "PROVIDERS_CONFIG",
    "CELERY_CONFIG",
    "QBT_CONFIG",
    "AUTH_CONFIG",
]
