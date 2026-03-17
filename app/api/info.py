"""
Info API routes
Public entry point — exposes API metadata and OpenAPI documentation links.
"""
from flask import jsonify, Response
from flask_smorest import Blueprint
from app.core.configs import APP_CONFIG, PROVIDERS_CONFIG

info_bp: Blueprint = Blueprint(
    "info",
    __name__,
    description="API metadata and documentation entry point",
)


@info_bp.route("/", methods=["GET"])
def get_public_config() -> tuple[Response, int]:
    """
    API entry point — public metadata + links to OpenAPI spec and Swagger UI.
    No authentication required.
    """
    base_api: str = APP_CONFIG["app"]["url"] + "/api"
    pagination = PROVIDERS_CONFIG["pagination"]
    return jsonify({
        "version": APP_CONFIG["version"],
        "environment": APP_CONFIG["app"]["env"],
        "docs": f"{base_api}/docs",
        "openapi_spec": f"{base_api}/openapi.json",
        "pagination": {
            "max_total_results": pagination["max_total_results"],
            "page_size": 20,
        },
    }), 200
