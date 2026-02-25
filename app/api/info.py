"""
Info API routes
Public endpoints for frontend configuration
"""
from flask import (Blueprint, jsonify, Response)
from app.api.settings import app_settings as settings

info_bp: Blueprint = Blueprint("info", __name__)


@info_bp.route("/", methods=["GET"])
def get_public_config() -> tuple[Response, int]:
    """
    Get public configuration for frontend
    No authentication required - only public URLs
    ---
    GET /api/info
    """
    return jsonify({
        "apiUrl": settings.get("API_URL", "http://localhost/") + "api",
        "version": settings.get("VERSION", "1.0.0"),
        "environment": settings.get("ENV", "dev")
    }), 200
