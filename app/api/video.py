"""Videos API - Unified endpoint for movies and TV shows"""
from flask import (
    Blueprint,
    jsonify,
    request,
    Response,
)
from app.core.errors import APIError
from app.services.video.models import ContentType
from app.services import (
    MovieService,
    TVShowService
)
from app.api.decorators.require_json import require_json
from app.api.decorators.require_auth import require_auth

video_bp = Blueprint("videos", __name__)

movie_service = MovieService()
tvshow_service = TVShowService()


@video_bp.route("/", methods=["GET"])
@require_auth
def get_all_videos() -> tuple[Response, int]:
    """Get all videos from database"""
    content_type: str = request.args.get("content_type", "all")
    if content_type == "all":
        movies: list[dict] = movie_service.get_all()
        tvshows: list[dict] = tvshow_service.get_all()
        videos: list[dict] = movies + tvshows
        return jsonify({
            "videos": videos,
            "total": len(videos),
            "movies_count": len(movies),
            "tvshows_count": len(tvshows)
        }), 200
    service: MovieService | TVShowService = _get_service(content_type)
    videos = service.get_all()
    return jsonify({
        "videos": videos,
        "total": len(videos),
        "content_type": content_type
    }), 200


@video_bp.route("/<int:video_id>", methods=["GET"])
@require_auth
def get_video(video_id: int) -> tuple[Response, int]:
    """Get a video by ID with full details"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    result = service.get_by_id(video_id)
    if result is None:
        raise APIError(404, "Video not found")
    return jsonify(result), 200


@video_bp.route("/<int:video_id>", methods=["PATCH"])
@require_json
@require_auth
def update_video(video_id: int) -> tuple[Response, int]:
    """Update a video"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    data = request.get_json()
    updated = service.update(video_id, data)
    if updated is None:
        raise APIError(404, "Video not found")
    return jsonify(updated), 200


@video_bp.route("/<int:video_id>", methods=["DELETE"])
@require_auth
def delete_video(video_id: int) -> tuple[Response, int]:
    """Delete a video"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    if not service.delete(video_id):
        raise APIError(404, "Video not found")
    return jsonify({"message": "Video deleted successfully"}), 200


@video_bp.route("/downloaded", methods=["GET"])
@require_auth
def get_downloaded_videos() -> tuple[Response, int]:
    """Get all downloaded videos"""
    content_type: str = request.args.get("content_type", "all")
    if content_type == "all":
        movies: list = movie_service.get_downloaded()
        tvshows: list = tvshow_service.get_downloaded()
        videos: list = [v.to_dict() for v in (movies + tvshows)]
        return jsonify({"videos": videos, "total": len(videos)}), 200
    service: MovieService | TVShowService = _get_service(content_type)
    videos: list = [v.to_dict() for v in service.get_downloaded()]
    return jsonify({
        "videos": videos,
        "total": len(videos),
        "content_type": content_type
    }), 200


@video_bp.route("/stats", methods=["GET"])
@require_auth
def get_video_stats() -> tuple[Response, int]:
    """Get statistics about videos"""
    content_type: str = request.args.get("content_type", "all")
    if content_type == "all":
        return jsonify({
            "movies": movie_service.get_statistics(),
            "tvshows": tvshow_service.get_statistics()
        }), 200
    service: MovieService | TVShowService = _get_service(content_type)
    return jsonify(service.get_statistics()), 200


@video_bp.route("/download", methods=["POST"])
@require_json
@require_auth
def download_video() -> tuple[Response, int]:
    """Start downloading a video via Celery"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    data = request.get_json()
    result = service.start_download(data)
    if result is None:
        raise APIError(500, "Download failed")
    return jsonify(result), 201


@video_bp.route("/<int:video_id>/status", methods=["GET"])
@require_auth
def get_video_status(video_id: int) -> tuple[Response, int]:
    """Get download status of a video"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    status = service.get_download_status(video_id)
    if status is None:
        raise APIError(404, "Video not found")
    return jsonify(status), 200


@video_bp.route("/<int:video_id>/pause", methods=["POST"])
@require_auth
def pause_download(video_id: int) -> tuple[Response, int]:
    """Pause video download"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    result = service.pause_download(video_id)
    if result is None:
        raise APIError(404, "Video not found")
    return jsonify(result), 200


@video_bp.route("/<int:video_id>/resume", methods=["POST"])
@require_auth
def resume_download(video_id: int) -> tuple[Response, int]:
    """Resume video download"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    result = service.resume_download(video_id)
    if result is None:
        raise APIError(404, "Video not found")
    return jsonify(result), 200


@video_bp.route("/<int:video_id>/stream", methods=["GET"])
@require_auth
def stream_video(video_id: int) -> Response:
    """Stream a downloaded video"""
    content_type: str = _require_content_type()
    service: MovieService | TVShowService = _get_service(content_type)
    stream_response = service.stream_video(video_id)
    if stream_response is None:
        raise APIError(404, "Video not found or not ready for streaming")
    return stream_response


def _require_content_type() -> str:
    """Extract and validate content_type from request args"""
    content_type: str = request.args.get("content_type")
    if not content_type:
        raise APIError(400, "content_type query parameter is required")
    return content_type


def _get_service(content_type: str) -> object:
    """Get appropriate service based on content type"""
    match content_type:
        case ContentType.MOVIE.value | "movie":
            return movie_service
        case ContentType.TV_SHOW.value | "tv_show":
            return tvshow_service
        case _:
            raise APIError(400, f"Invalid content_type: {content_type}")
