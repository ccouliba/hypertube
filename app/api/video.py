"""Videos API — unified endpoint for movies and TV shows"""
import os
import logging
from pathlib import Path
from typing import Optional, Union
from flask import Response, jsonify, make_response, request
from flask_smorest import Blueprint
from app.core.errors import APIError
from app.core.errors.messages import ERROR_MESSAGES
from app.services.video.models import ContentType
from app.services import MovieService, TVShowService
from app.api.decorators.require_auth import require_auth
from app.api.decorators.require_stream_auth import require_stream_auth
from app.schemas import (
    ContentTypeQuerySchema,
    OptionalContentTypeQuerySchema,
    VideoSchema,
    VideoStatusSchema,
    VideoListResponseSchema,
    DownloadVideoSchema,
    DownloadResponseSchema,
    MessageSchema,
)
from app.schemas.video_schemas import UpdateVideoSchema

video_bp: Blueprint = Blueprint(
    "videos",
    __name__,
    description="Video content: listing, download and streaming",
)

movie_service: MovieService = MovieService()
tvshow_service: TVShowService = TVShowService()

LOGGER = logging.getLogger(__name__)
_USE_NGINX: bool = os.getenv("NGINX_STREAMING_ENABLED", "false").lower() == "true"
_DOWNLOADS_ROOT: str = "/downloads"
_NGINX_INTERNAL_PREFIX: str = "/internal-downloads"
_NGINX_NATIVE_EXTS: frozenset[str] = frozenset({".mp4", ".webm", ".ogg"})


@video_bp.route("/", methods=["GET"])
@video_bp.arguments(OptionalContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoListResponseSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_all_videos(q: dict) -> dict:
    """Get all videos from database"""
    content_type: str = q["content_type"]
    if content_type == "all":
        movies: list[dict] = movie_service.get_all()
        tvshows: list[dict] = tvshow_service.get_all()
        videos: list[dict] = movies + tvshows
        return {
            "videos": videos,
            "total": len(videos),
            "movies_count": len(movies),
            "tvshows_count": len(tvshows),
        }
    service: Union[MovieService, TVShowService] = _get_service(content_type)
    videos: list[dict] = service.get_all()
    return {"videos": videos, "total": len(videos), "content_type": content_type}


@video_bp.route("/<int:video_id>", methods=["GET"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_video(q: dict, video_id: int) -> dict:
    """Get a video by ID with full details"""
    service: Union[MovieService, TVShowService] = _get_service(q["content_type"])
    result: Optional[dict] = service.get_by_id(video_id)
    if result is None:
        raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
    return result


@video_bp.route("/<int:video_id>", methods=["PATCH"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.arguments(UpdateVideoSchema)
@video_bp.response(200, VideoSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def update_video(q: dict, body: dict, video_id: int) -> dict:
    """Update a video"""
    service: Union[MovieService, TVShowService] = _get_service(q["content_type"])
    updated: Optional[dict] = service.update(video_id, body)
    if updated is None:
        raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
    return updated


@video_bp.route("/<int:video_id>", methods=["DELETE"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.response(200, MessageSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def delete_video(q: dict, video_id: int) -> dict:
    """Delete a video"""
    service: Union[MovieService, TVShowService] = _get_service(q["content_type"])
    service.delete(video_id)
    return {"message": "Video deleted successfully"}


@video_bp.route("/downloaded", methods=["GET"])
@video_bp.arguments(OptionalContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoListResponseSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_downloaded_videos(q: dict) -> dict:
    """Get all downloaded videos"""
    content_type: str = q["content_type"]
    if content_type == "all":
        movies: list[dict] = movie_service.get_downloaded()
        tvshows: list[dict] = tvshow_service.get_downloaded()
        videos: list[dict] = [v.to_dict() for v in (movies + tvshows)]
        return {"videos": videos, "total": len(videos)}
    service: Union[MovieService, TVShowService] = _get_service(content_type)
    videos: list[dict] = [v.to_dict() for v in service.get_downloaded()]
    return {"videos": videos, "total": len(videos), "content_type": content_type}


@video_bp.route("/stats", methods=["GET"])
@video_bp.arguments(OptionalContentTypeQuerySchema, location="query")
@video_bp.doc(
    security=[{"BearerAuth": []}],
    responses={200: {"description": "Video statistics"}},
)
@require_auth
def get_video_stats(q: dict):
    """Get statistics about videos"""
    content_type: str = q["content_type"]
    if content_type == "all":
        return jsonify({
            "movies": movie_service.get_statistics(),
            "tvshows": tvshow_service.get_statistics(),
        }), 200
    return jsonify(_get_service(content_type).get_statistics()), 200


@video_bp.route("/download", methods=["POST"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.arguments(DownloadVideoSchema)
@video_bp.response(201, DownloadResponseSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def download_video(q: dict, body: dict) -> dict:
    """Start downloading a video via Celery"""
    result: Optional[dict] = _get_service(q["content_type"]).start_download(body)
    if result is None:
        raise APIError(500, "Download failed")
    return result


@video_bp.route("/<int:video_id>/status", methods=["GET"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoStatusSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_video_status(q: dict, video_id: int) -> dict:
    """Get download status of a video"""
    status: Optional[dict] = _get_service(q["content_type"]).get_download_status(video_id)
    if status is None:
        raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
    return status


@video_bp.route("/<int:video_id>/pause", methods=["POST"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def pause_download(q: dict, video_id: int) -> dict:
    """Pause video download"""
    result: Optional[dict] = _get_service(q["content_type"]).pause_download(video_id)
    if result is None:
        raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
    return result


@video_bp.route("/<int:video_id>/resume", methods=["POST"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.response(200, VideoSchema)
@video_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def resume_download(q: dict, video_id: int) -> dict:
    """Resume video download"""
    result: Optional[dict] = _get_service(q["content_type"]).resume_download(video_id)
    if result is None:
        raise APIError(404, ERROR_MESSAGES["VIDEO_NOT_FOUND"])
    return result


@video_bp.route("/<int:video_id>/stream", methods=["GET"])
@video_bp.arguments(ContentTypeQuerySchema, location="query")
@video_bp.doc(
    responses={200: {"description": "Video stream (video/mp4)"}},
)
@require_stream_auth
def stream_video(q: dict, video_id: int) -> Response:
    """Stream a video.
    Native formats (mp4/webm/ogg) running behind nginx:
        Flask validates auth + resolves file path, then returns X-Accel-Redirect.
        nginx intercepts the header and serves the file via sendfile(2) — zero Python I/O.
    Non-native formats (mkv/avi/…) or local dev without nginx:
        Falls back to Flask FFmpeg remux streaming.
    """
    service: Union[MovieService, TVShowService] = _get_service(q["content_type"])
    file_path: str = service.get_file_path_for_streaming(video_id)
    ext: str = Path(file_path).suffix.lower()
    if _USE_NGINX and ext in _NGINX_NATIVE_EXTS:
        # Security: reject any path that escaped the downloads directory.
        if not file_path.startswith(_DOWNLOADS_ROOT + "/"):
            LOGGER.error("stream_video: file path outside downloads root: %s", file_path)
            raise APIError(500, "Unexpected file location")
        internal_path: str = _NGINX_INTERNAL_PREFIX + file_path[len(_DOWNLOADS_ROOT):]
        LOGGER.debug("stream_video: X-Accel-Redirect → %s", internal_path)
        resp: Response = make_response("", 200)
        resp.headers["X-Accel-Redirect"] = internal_path
        resp.headers["Content-Type"] = ""
        return resp
    LOGGER.debug("stream_video: Flask fallback for %s (nginx=%s)", ext, _USE_NGINX)
    return service.stream_video(video_id, request.headers.get("Range"))


def _get_service(content_type: str) -> MovieService | TVShowService:
    """Return the appropriate service instance for the given content type."""
    match content_type:
        case ContentType.MOVIE.value | "movie":
            return movie_service
        case ContentType.TV_SHOW.value | "tv_show":
            return tvshow_service
        case _:
            raise APIError(400, f"Invalid content_type: {content_type}")
