"""Cors - Cross-Origin Resource Sharing"""

from flask import Flask
from flask_cors import CORS


def define_CORS(app: Flask) -> None:
    """Define CORS settings for the Flask app"""

    from app.core.configs import APP_CONFIG
    
    CORS(app, resources={
        r"/api/*": {
            "origins": APP_CONFIG["local_urls"],
            "methods": APP_CONFIG["allowed_methods"],
            "allow_headers": APP_CONFIG["allowed_headers"],
            "supports_credentials": APP_CONFIG["supports_credentials"],
        }
    })
