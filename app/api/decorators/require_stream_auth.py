"""Stream auth decorator — validates stream_token HttpOnly cookie"""
import jwt
from functools import wraps
from flask import request, g
from app.core.errors import APIError
from app.core.security.jwt_gen import decode_token

_STREAM_TOKEN_NAME = "stream_token"


def require_stream_auth(f):
    """Decorator for the stream endpoint: authenticates via HttpOnly cookie
    instead of the Authorization header (browsers can't set headers on <video> requests)."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        token: str | None = request.cookies.get(_STREAM_TOKEN_NAME)
        if not token:
            raise APIError(401, "Missing stream token cookie")
        try:
            payload: dict = decode_token(token)
            g.user_id = payload.get("user_id")
            g.username = payload.get("username")
        except APIError:
            raise
        except jwt.ExpiredSignatureError:
            raise APIError(401, "Stream token has expired")
        except jwt.InvalidTokenError:
            raise APIError(401, "Invalid stream token")
        except RuntimeError as e:
            raise APIError(500, str(e))
        return f(*args, **kwargs)

    return decorated_function
