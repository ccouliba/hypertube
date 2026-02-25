"""Search API routes"""
from flask import (
    Blueprint,
    request,
    jsonify,
    Response
)
from app.core.errors import APIError
from app.api.decorators.require_auth import require_auth
from app.services import SearchService
from app.services.search import providers_settings

search_bp: Blueprint = Blueprint("search", __name__)
YTS_NAME: str = providers_settings["YTS_NAME"]
EZTV_NAME: str = providers_settings["EZTV_NAME"]
MAX_PER_PAGE: int = providers_settings["RESULTS_MAX_PER_PAGE"]
MAX_TOTAL: int = providers_settings["RESULTS_TOTAL_RESULTS"]

search_service: SearchService = SearchService()


@search_bp.route("/", methods=["GET"])
@require_auth
def search_videos() -> tuple[Response, int]:
    """
    Search movies by title from local database and external sources
    If no query provided, returns popular movies and TV shows
    ---
    GET /api/search?query=inception (search)
    GET /api/search (popular content)
    Optional: page, limit for pagination
    """
    query: str = request.args.get("query", "").strip()
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(MAX_TOTAL, max(1, int(request.args.get("limit", MAX_PER_PAGE))))
    except (ValueError, TypeError):
        raise APIError(
            400,
            "Invalid pagination parameters"
        )
    if query and len(query) < 2:
        raise APIError(
            400,
            "Search query must be at least 2 characters"
        )
    results: dict = search_service.unified_search(query, page, limit)
    return jsonify(results), 200


@search_bp.route("/providers", methods=["GET"])
def get_providers() -> tuple[Response, int]:
    """Get list of available search providers"""
    return jsonify({
        "providers": [
            {
                "name": YTS_NAME,
                "description": "HQ movies torrents",
                "status": "active"
            },
            {
                "name": EZTV_NAME,
                "description": "TV Shows torrents",
                "status": "active"
            }
        ]
    }), 200
