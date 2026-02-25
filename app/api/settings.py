"""Info API routes settings module
"""
from app.core.configs import APP_CONFIG as app_config

app_settings: dict[str, any] = {
    "API_URL": str(app_config["app"]["url"]),
    "VERSION": str(app_config["version"]),
    "ENV": str(app_config["app"]["env"]),
}
