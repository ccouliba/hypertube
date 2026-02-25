"""Application-level settings module"""
from app.core.configs import APP_CONFIG as app_config

app_settings: dict[str, any] = {
    """Application settings dictionary"""

    "ENV": str(app_config["app"]["env"]),
    "API_HOST": str(app_config["api"]["host"]),
    "API_PORT": int(app_config["api"]["port"]),
    "DEBUG": bool(app_config["debug"]),
    "LOCAL_URLS": list[str](app_config["local_urls"]),
    "METHODS": list[str](app_config["allowed_methods"]),
    "HEADERS": list[str](app_config["allowed_headers"]),
    "CREDENTIALS": bool(app_config["supports_credentials"]),
}
