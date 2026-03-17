"""Auth API routes"""
import os
from datetime import timedelta
from flask import (Response, request, make_response, g)
from flask_smorest import Blueprint
from app.services import AuthService
from app.api.decorators.require_auth import require_auth
from app.core.configs import AUTH_CONFIG
from app.core.errors import APIError
from app.core.security import limiter
from app.core.security.jwt_gen import generate_token
from app.schemas import (
    RegisterSchema,
    LoginSchema,
    UpdateUserSchema,
    LoginResponseSchema,
    AccessTokenResponseSchema,
    RegisterResponseSchema,
    UpdateUserResponseSchema,
    UsersListResponseSchema,
    UserPublicSchema,
    MessageSchema,
)

auth_bp: Blueprint = Blueprint(
    "auth",
    __name__,
    description="User authentication and account management",
)
auth_service: AuthService = AuthService()


_COOKIE_NAME: str = "refresh_token"
_REFRESH_EXPIRES_DAYS: int = int(AUTH_CONFIG["jwt"]["refresh_token_expires_days"])
_COOKIE_MAX_AGE: int = int(_REFRESH_EXPIRES_DAYS * 24 * 3600)

_STREAM_TOKEN_NAME: str = "stream_token"
_STREAM_TOKEN_MAX_AGE: int = 3600


@auth_bp.route("/register", methods=["POST"])
# @limiter.limit("5 per hour")
@auth_bp.arguments(RegisterSchema)
@auth_bp.response(201, RegisterResponseSchema)
def register(body: dict) -> dict:
    """Register a new user"""
    return auth_service.register_user(body)


@auth_bp.route("/login", methods=["POST"])
# @limiter.limit("10 per minute")
@auth_bp.arguments(LoginSchema)
@auth_bp.response(200, LoginResponseSchema)
def login(body: dict) -> Response:
    """Authenticate user — returns a short-lived JWT + sets a httpOnly refresh token cookie"""
    result: dict = auth_service.authenticate_user(body)
    raw_refresh: str = result.pop("raw_refresh_token")  # not exposed in response body
    response: Response = make_response(result, 200)
    return _set_refresh_cookie(response, raw_refresh)


@auth_bp.route("/refresh", methods=["POST"])
@auth_bp.response(200, AccessTokenResponseSchema)
def refresh() -> Response:
    """
    Issue a new access token using the httpOnly refresh token cookie.
    Implements rotation: the old refresh token is revoked and a new one is set.
    Clears the cookie if the token is invalid/expired so the browser stops sending it.
    """
    raw_token: str = request.cookies.get(_COOKIE_NAME, "")
    try:
        result: dict = auth_service.refresh_access_token(raw_token)
    except APIError as e:
        response: Response = make_response({"message": e.message}, e.code)
        _clear_refresh_cookie(response)
        return response
    new_raw_refresh: str = result.pop("raw_refresh_token")
    response: Response = make_response(result, 200)
    return _set_refresh_cookie(response, new_raw_refresh)


@auth_bp.route("/logout", methods=["POST"])
@auth_bp.response(200, MessageSchema)
def logout() -> Response:
    """Revoke the refresh token and clear the cookie (server-side logout)"""
    raw_token: str = request.cookies.get(_COOKIE_NAME, "")
    result: dict = auth_service.logout_user(raw_token)
    response: Response = make_response(result, 200)
    return _clear_refresh_cookie(response)


@auth_bp.route("/users", methods=["GET"])
@auth_bp.response(200, UsersListResponseSchema)
@auth_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_users() -> dict:
    """Get the list of all users"""
    return {"users": auth_service.get_all_users()}


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
@auth_bp.response(200, UserPublicSchema)
@auth_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def get_user(user_id: int) -> dict:
    """Get a user by ID"""
    return auth_service.get_user_by_id(user_id, request.host_url.rstrip("/"))


@auth_bp.route("/users/<int:user_id>", methods=["PATCH"])
@auth_bp.arguments(UpdateUserSchema)
@auth_bp.response(200, UpdateUserResponseSchema)
@auth_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def update_user(body: dict, user_id: int) -> dict:
    """Update a user's information"""
    return auth_service.update_user_by_id(user_id, body)


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
@auth_bp.response(200, MessageSchema)
@auth_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def delete_user(user_id: int) -> dict:
    """Delete a user by ID"""
    return auth_service.delete_user_by_id(user_id)


@auth_bp.route("/stream-token", methods=["POST"])
@auth_bp.response(200, MessageSchema)
@auth_bp.doc(security=[{"BearerAuth": []}])
@require_auth
def issue_stream_token() -> Response:
    """Issue a short-lived HttpOnly cookie for video streaming.
    Called by the front just before opening the player.
    The cookie (path=/api/video) is sent automatically by the browser on <video> requests.
    """
    secret: str | None = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise APIError(500, "JWT_SECRET_KEY is not set")
    token: str = generate_token(
        {"user_id": g.user_id, "username": g.username},
        timedelta(seconds=_STREAM_TOKEN_MAX_AGE),
        secret,
    )
    response: Response = make_response({"message": "Stream token issued"}, 200)
    response.set_cookie(
        _STREAM_TOKEN_NAME,
        value=token,
        max_age=_STREAM_TOKEN_MAX_AGE,
        httponly=True,
        samesite="Strict",
        # secure=True  # uncomment in production (requires HTTPS)
        path="/api/video",
    )
    return response


def _set_refresh_cookie(response: Response, raw_token: str) -> Response:
    """Attach the refresh token as an httpOnly cookie to a response"""
    response.set_cookie(
        _COOKIE_NAME,
        value=raw_token,
        max_age=_COOKIE_MAX_AGE,
        httponly=True,
        samesite="Strict",
        # secure=True  # uncomment in production (requires HTTPS)
        path="/api/auth",  # cookie is only sent to auth endpoints
    )
    return response


def _clear_refresh_cookie(response: Response) -> Response:
    """Delete the refresh token cookie"""
    response.delete_cookie(_COOKIE_NAME, path="/api/auth")
    return response

