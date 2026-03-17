"""Marshmallow schemas — single source of truth for API contracts"""
from app.schemas.auth_schemas import (
    RegisterSchema,
    LoginSchema,
    UpdateUserSchema,
    UserPublicSchema,
    UserMiniSchema,
    LoginResponseSchema,
    AccessTokenResponseSchema,
    RegisterResponseSchema,
    UpdateUserResponseSchema,
    UsersListResponseSchema,
    MessageSchema,
)
from app.schemas.video_schemas import (
    VideoSchema,
    VideoStatusSchema,
    VideoListResponseSchema,
    DownloadVideoSchema,
    ContentTypeQuerySchema,
    OptionalContentTypeQuerySchema,
    DownloadResponseSchema,
)
from app.schemas.search_schemas import SearchQuerySchema

__all__ = [
    # Auth
    "RegisterSchema",
    "LoginSchema",
    "UpdateUserSchema",
    "UserPublicSchema",
    "UserMiniSchema",
    "LoginResponseSchema",
    "AccessTokenResponseSchema",
    "RegisterResponseSchema",
    "UpdateUserResponseSchema",
    "UsersListResponseSchema",
    "MessageSchema",
    # Video
    "VideoSchema",
    "VideoStatusSchema",
    "VideoListResponseSchema",
    "DownloadVideoSchema",
    "ContentTypeQuerySchema",
    "OptionalContentTypeQuerySchema",
    "DownloadResponseSchema",
    # Search
    "SearchQuerySchema",
]
