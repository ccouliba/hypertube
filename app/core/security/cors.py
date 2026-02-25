"""Cors - Cross-Origin Resource Sharing"""

from flask import Flask
from flask_cors import CORS


def define_CORS(app: Flask) -> None:
    """Define CORS settings for the Flask app"""

    from app import app_settings as settings
    
    CORS(app, resources={
    r"/api/*": {
            "origins": settings.get("LOCAL_URLS", []) + settings.get("EXTERNAL_URLS", []),
            "methods": settings.get("METHODS", []),
            "allow_headers": settings.get("HEADERS", []),
            "supports_credentials": settings.get("CREDENTIALS", False)
        }
    })
