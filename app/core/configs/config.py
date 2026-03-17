"""Centralized application configuration

All environment-based settings live here. Import from `app.core.configs` (the package)
rather than from this file directly.
"""
import os

# ---------------------------------------------------------------------------
# General / App
# ---------------------------------------------------------------------------
APP_CONFIG: dict = {
    "app": {
        "url": os.getenv("APP_URL", "http://localhost:5000"),
        "content_type": os.getenv("CONTENT_TYPE", "application/json"),
        "env": os.getenv("FLASK_ENV", "dev"),
    },
    "api": {
        "host": os.getenv("API_HOST", "0.0.0.0"),
        "port": int(os.getenv("API_PORT", "5000")),
    },
    "local_urls": [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5000",
        "http://127.0.0.1:5000",
    ],
    "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    "allowed_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "version": "1.0.0",
    # OpenAPI / Swagger
    "openapi": {
        "title": os.getenv("API_TITLE", "Hypertube API"),
        "version": os.getenv("API_VERSION", "v1"),
        "openapi_version": os.getenv("OPENAPI_VERSION", "3.0.3"),
        "url_prefix": os.getenv("OPENAPI_URL_PREFIX", "/api"),
        "swagger_ui_path": os.getenv("OPENAPI_SWAGGER_UI_PATH", "/docs"),
        "swagger_ui_url": os.getenv(
            "OPENAPI_SWAGGER_UI_URL",
            "https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
        ),
        "api_type": os.getenv("API_TYPE", "http"),
        "token_schemes": os.getenv("TOKEN_SCHEME", "bearer"),
        "bearer_format": os.getenv("BEARER_FORMAT", "JWT"),
    },
}

# ---------------------------------------------------------------------------
# Database (SQLAlchemy / PostgreSQL)
# ---------------------------------------------------------------------------
DB_CONFIG: dict = {
    "sqlalchemy": {
        "echo": os.getenv("SQLALCHEMY_ECHO", "False").lower() == "true",
        "track_modifications": os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False").lower() == "true",
    },
    "db": {
        "user": os.getenv("DB_USER", "hypertube"),
        "password": os.getenv("DB_PASSWORD", ""),
        "host": os.getenv("DB_HOST", "database"),
        "port": int(os.getenv("DB_PORT") or "5432"),
        "name": os.getenv("DB_NAME", "hypertube"),
    },
}

# ---------------------------------------------------------------------------
# Auth (JWT + OAuth + validation rules)
# ---------------------------------------------------------------------------
AUTH_CONFIG: dict = {
    "jwt": {
        "secret_key": os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production"),
        "algorithm": "HS256",
        # Access token: short-lived JWT (in memory on client)
        "access_token_expires_minutes": int(os.getenv("JWT_ACCESS_EXPIRES_MINUTES", "15")),
        # Refresh token: long-lived opaque token (httpOnly cokie)
        "refresh_token_expires_days": int(os.getenv("JWT_REFRESH_EXPIRES_DAYS", "30")),
    },
    "oauth": {
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "github_client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "github_client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "42_client_id": os.getenv("INTRA_42_CLIENT_ID", ""),
        "42_client_secret": os.getenv("INTRA_42_CLIENT_SECRET", ""),
    },
    "username": {
        "min_length": int(os.getenv("USERNAME_MIN_LENGTH", "2")),
        "max_length": int(os.getenv("USERNAME_MAX_LENGTH", "20")),
        "authorized_characters": os.getenv("USERNAME_AUTHORIZED_CHARACTERS", r'^[a-zA-Z0-9_-]+$'),
    },
    "password": {
        "min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "6")),
        "require_uppercase": os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
        "require_lowercase": os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
        "require_digit": os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true",
        "require_letter": os.getenv("PASSWORD_REQUIRE_LETTER", "true").lower() == "true",
        "require_special": os.getenv("PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true",
        "special_characters": os.getenv("SPECIAL_CHARACTERS", r'[!@#$%^&*(),.?":{}|<>]'),
    },
    "session": {
        "timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "120")),
    },
    "supported_languages": os.getenv("SUPPORTED_LANGUAGES", "en,fr").split(","),
}

# ---------------------------------------------------------------------------
# Redis (shared across Celery broker, result backend, rate limiter, search cache)
# ---------------------------------------------------------------------------
_REDIS_BASE: str = os.getenv("REDIS_URL", "redis://redis:6379/")

REDIS_CONFIG: dict = {
    "base_url": _REDIS_BASE,
    "db": {
        "celery_broker":  1,
        "celery_result":  2,
        "rate_limiter":   3,
        "search_cache":   4,
    },
}

# ---------------------------------------------------------------------------
# Celery / Redis
# ---------------------------------------------------------------------------
_REDIS_BASE_URL: str = _REDIS_BASE

CELERY_CONFIG: dict = {
    "broker": {
        "url": os.getenv("CELERY_BROKER_URL", _REDIS_BASE + str(REDIS_CONFIG["db"]["celery_broker"])),
        "result_backend": os.getenv("CELERY_RESULT_BACKEND", _REDIS_BASE + str(REDIS_CONFIG["db"]["celery_result"])),
        "connection_retry_on_startup": True,
    },
    "task": {
        "serializer": "json",
        "accept_content": ["json"],
        "result_serializer": "json",
        "task_track_started": True,
        # 30 * 60 seconds = 30 minutes
        "task_time_limit": int(os.getenv("TASK_TIME_LIMIT", "1800")),
        # 25 * 60 seconds = 25 minutes
        "task_soft_time_limit": int(os.getenv("TASK_SOFT_TIME_LIMIT", "1500")),
    },
    "retry": {
        "countdown": int(os.getenv("TASK_RETRY_COUNTDOWN", "60")),
        "max_retries": int(os.getenv("TASK_RETRY_MAX", "3")),
    },
    "maintenance": {
        "cleanup_days": int(os.getenv("CLEANUP_OLD_MOVIES_DAYS", "30")),
        "cleanup_hour": int(os.getenv("CLEANUP_HOUR", "11")),
        "cleanup_minute": int(os.getenv("CLEANUP_MINUTE", "0")),
    },
    "timezone": "UTC",
    "enable_utc": True,
    "result_backend_expires": int(os.getenv("CELERY_RESULT_BACKEND_EXPIRES", "3600")),  # 1 hour
    "worker": {
        "prefetch_multiplier": int(os.getenv("CELERY_WORKER_PREFETCH_MULTIPLIER", "4")),
        "max_tasks_per_child": int(os.getenv("CELERY_WORKER_MAX_TASKS_PER_CHILD", "1000")),
        "log_level": os.getenv("CELERY_WORKER_LEVEL", "INFO"),
        "log_format": "[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
        "task_log_format": "[%(asctime)s: %(levelname)s/%(processName)s][%(task_name)s(%(task_id)s)] %(message)s",
        "redirect_stdouts": True,
        "redirect_stdouts_level": os.getenv("CELERY_WORKER_LEVEL", "INFO"),
    },
}

# ---------------------------------------------------------------------------
# qBittorrent
# ---------------------------------------------------------------------------
QBT_CONFIG: dict = {
    "qbittorrent": {
        "host": os.getenv("QBITTORRENT_HOST", "http://qbittorrent:8080"),
        "user": os.getenv("QBITTORRENT_USER", "admin"),
        "pass": os.getenv("QBITTORRENT_PASS", "secret123"),
        "timeout": int(os.getenv("QB_TIMEOUT", "30")),
    },
    "downloads": {
        "directory": os.getenv("DOWNLOAD_DIR", "/downloads"),
        "max_concurrent": int(os.getenv("MAX_CONCURRENT_DOWNLOADS", "5")),
    },
    "video": {
        "extensions": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
        "min_size_mb": int(os.getenv("MIN_VIDEO_SIZE_MB", "100")),
    },
}

# ---------------------------------------------------------------------------
# Search providers (YTS, EZTV, TMDb)
# ---------------------------------------------------------------------------
PROVIDERS_CONFIG: dict = {
    "yts": {
        "name": "YTS",
        "content": "movie",
        "base_url": os.getenv("YTS_BASE_URL", "https://yts.lt/api/v2"),
        "list_movies": "list_movies.json",
        "enabled": os.getenv("YTS_ENABLED", "true").lower() == "true",
    },
    "eztv": {
        "name": "EZTV",
        "content": "tv_show",
        "base_url": os.getenv("EZTV_BASE_URL", "https://eztvx.to/api"),
        "get_torrents": "get-torrents",
        "enabled": os.getenv("EZTV_ENABLED", "true").lower() == "true",
    },
    "tmdb": {
        "name": "TMDb",
        "base_url": os.getenv("TMDB_BASE_URL", "https://api.themoviedb.org/3"),
        "api_key": os.getenv("TMDB_API_KEY", ""),
        "image_base_url": os.getenv("TMDB_IMAGE_BASE_URL", "https://image.tmdb.org/t/p"),
        "search_video": "search/movie",
        "search_tv": "search/tv",
        "poster_size": "w500",
        "backdrop_size": "original",
        "enabled": os.getenv("TMDB_ENABLED", "true").lower() == "true",
    },
    "timeout": {
        "default": int(os.getenv("PROVIDER_TIMEOUT", "10")),
        "search": int(os.getenv("SEARCH_TIMEOUT", "15")),
    },
    "pagination": {
        "max_per_page": int(os.getenv("PER_PAGE", "50")),
        "max_results_per_provider": int(os.getenv("MAX_RESULTS_PER_PROVIDER", "30")),
        "max_total_results": int(os.getenv("MAX_TOTAL_RESULTS", "100")),
    },
    "cache": {
        "ttl": int(os.getenv("CACHE_TTL_SECONDS", "86400")),
    },
}
