"""API - Application programming interface package utilities

Provides:
- API initialization for AuthAPI, VideoAPI and SearchAPI
- Blueprint definitions
"""
from app.api.auth import auth_bp
from app.api.video import video_bp
from app.api.search import search_bp
from app.api.info import info_bp
from app.api.decorators.require_auth import require_auth
from app.api.decorators.require_json import require_json

__all__ = [
    "auth_bp",
    "video_bp",
    "search_bp",
    "info_bp",
    "require_auth",
    "require_json",
]
