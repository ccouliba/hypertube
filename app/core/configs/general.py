"""Global application configurations"""
import os

G_CONFIG: dict[str, any] = {
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
        "http://127.0.0.1:5000"
    ],
    "allowed_methods": [
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS"
    ],
    "allowed_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True,
    "debug": os.getenv("DEBUG", "True").lower() == "true",
    "version": "1.0.0",
}
