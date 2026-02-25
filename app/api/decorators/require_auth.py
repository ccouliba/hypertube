"""Auth domain decorators"""
import jwt
from functools import wraps
from flask import (request, g)
from app.services.auth.settings import auth_settings as settings
from app.core.errors import APIError

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
        try: # Format: "Bearer <token>"
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise APIError(
                    status_code=401,
                    message="Invalid authorization scheme"
                )
            secret_key: str = settings.get("SECRET_KEY", "default_secret")
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[settings.get("ALGORITHM", "HS256")]
            )
            g.user_id = payload.get("user_id")
            g.username = payload.get("username")
        except ValueError:
            raise APIError(
                status_code=401,
                message="Invalid authorization header format"
            )
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
        return f(*args, **kwargs)
    return decorated_function
