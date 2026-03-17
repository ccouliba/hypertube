"""Video domain Marshmallow schemas — validation + serialisation"""
from marshmallow import (Schema, fields, validate, EXCLUDE)


class ContentTypeQuerySchema(Schema):
    """Required content_type query parameter"""

    class Meta:
        unknown = EXCLUDE

    content_type = fields.Str(
        required=True,
        validate=validate.OneOf(
            ["movie", "tv_show"],
            error="content_type must be 'movie' or 'tv_show'",
        ),
    )


class OptionalContentTypeQuerySchema(Schema):
    """Optional content_type, defaults to 'all'"""

    class Meta:
        unknown = EXCLUDE

    content_type = fields.Str(
        load_default="all",
        validate=validate.OneOf(
            ["movie", "tv_show", "all"],
            error="content_type must be 'movie', 'tv_show' or 'all'",
        ),
    )


class DownloadVideoSchema(Schema):
    """Payload to initiate a torrent download"""

    class Meta:
        unknown = EXCLUDE

    title = fields.Str(required=True, validate=validate.Length(min=1))
    torrent_hash = fields.Str(required=True, validate=validate.Length(min=1))
    torrent_url = fields.Str(required=True, validate=validate.Length(min=1))
    year = fields.Int(load_default=None)
    rating = fields.Float(load_default=None)
    genres = fields.List(fields.Str(), load_default=[])
    synopsis = fields.Str(load_default=None)
    thumbnail = fields.Str(load_default=None)
    cover_image = fields.Str(load_default=None)
    provider = fields.Str(load_default="manual")


class UpdateVideoSchema(Schema):
    """Partial update payload for a video"""

    class Meta:
        unknown = EXCLUDE

    title = fields.Str(validate=validate.Length(min=1))
    year = fields.Int()
    rating = fields.Float()
    genres = fields.List(fields.Str())
    synopsis = fields.Str()


class VideoSchema(Schema):
    """Full video representation"""
    id = fields.Int()
    title = fields.Str()
    year = fields.Int(allow_none=True)
    rating = fields.Float(allow_none=True)
    genres = fields.List(fields.Str(), allow_none=True)
    synopsis = fields.Str(allow_none=True)
    thumbnail = fields.Str(allow_none=True)
    large_cover = fields.Str(allow_none=True)
    provider = fields.Str(allow_none=True)
    external_id = fields.Str(allow_none=True)
    tmdb_id = fields.Int(allow_none=True)
    content_type = fields.Str()
    downloaded = fields.Bool()
    download_status = fields.Str()
    download_progress = fields.Float()
    file_path = fields.Str(allow_none=True)
    created_at = fields.Str(allow_none=True)
    last_watched = fields.Str(allow_none=True)


class VideoListResponseSchema(Schema):
    videos = fields.List(fields.Nested(VideoSchema))
    total = fields.Int()
    movies_count = fields.Int(load_default=None, allow_none=True)
    tvshows_count = fields.Int(load_default=None, allow_none=True)
    content_type = fields.Str(load_default=None, allow_none=True)


class DownloadResponseSchema(Schema):
    message = fields.Str()
    video_id = fields.Int()
    task_id = fields.Str()
    video = fields.Nested(VideoSchema)


class VideoStatusSchema(Schema):
    """Response for the download-status endpoint"""
    video_id = fields.Int()
    status = fields.Str()
    progress = fields.Float()


class VideoStatsSchema(Schema):
    total = fields.Int()
    downloaded = fields.Int()
    downloading = fields.Int()
    not_downloaded = fields.Int()
