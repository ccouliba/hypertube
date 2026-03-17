"""Search API routes"""
from flask import jsonify
from flask_smorest import Blueprint
from app.core.errors import APIError
from app.core.errors.messages import ERROR_MESSAGES
from app.api.decorators.require_auth import require_auth
from app.services import SearchService
from app.services.search import providers_settings
from app.schemas import SearchQuerySchema

search_bp: Blueprint = Blueprint(
    "search",
    __name__,
    description="Search movies and TV shows from external providers",
)

YTS_NAME: str = providers_settings["YTS_NAME"]
EZTV_NAME: str = providers_settings["EZTV_NAME"]
search_service: SearchService = SearchService()


@search_bp.route("/", methods=["GET"])
@search_bp.arguments(SearchQuerySchema, location="query")
@search_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def search_videos(q: dict) -> tuple:
    """
    Search movies and TV shows.
    If no query is provided, returns popular content.
    """
    query: str = q.get("query", "").strip()
    if query and len(query) < 2:
        raise APIError(400, ERROR_MESSAGES["QUERY_TOO_SHORT"])
    return jsonify(search_service.unified_search(query, q["page"], q["limit"])), 200


@search_bp.route("/providers", methods=["GET"])
def get_providers() -> tuple:
    """Get the list of active search providers"""
    return jsonify({
        "providers": [
            {"name": YTS_NAME, "description": "HQ movies torrents", "status": "active"},
            {"name": EZTV_NAME, "description": "TV Shows torrents", "status": "active"},
        ]
    }), 200
