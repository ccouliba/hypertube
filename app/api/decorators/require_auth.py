"""Auth domain decorators"""
import jwt
from functools import wraps
from flask import (request, g)
from app.core.errors import APIError
from app.core.security.jwt_gen import decode_token


def require_auth(f):
    """Decorator to ensure request has valid JWT token"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header: str = request.headers.get("Authorization")
        if not auth_header:
            raise APIError(
                status_code=401,
                message="Missing authorization header"
            )
        try:
            parts: list[str] = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise APIError(
                    status_code=401,
                    message="Invalid authorization header format"
                )
            payload: dict = decode_token(parts[1])
            g.user_id = payload.get("user_id")
            g.username = payload.get("username")
        except APIError:
            raise
        except jwt.ExpiredSignatureError:
            raise APIError(
                status_code=401,
                message="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise APIError(
                status_code=401,
                message="Invalid token"
            )
        except RuntimeError as e:
            raise APIError(
                status_code=500,
                message=str(e)
            )
        return f(*args, **kwargs)
    
    return decorated_function
