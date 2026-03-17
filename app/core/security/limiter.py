"""Rate limiting - Flask-Limiter instance (factory pattern)"""
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.core.configs import REDIS_CONFIG

_db: int = REDIS_CONFIG["db"]["rate_limiter"]
_LIMITER_STORAGE_URI: str = REDIS_CONFIG["base_url"] + str(_db)


def _get_real_ip() -> str:
    """Return the real client IP from X-Real-IP (injected by nginx, not spoofable).
    Falls back to the TCP remote address in local dev where nginx is absent.
    """
    return request.headers.get("X-Real-IP") or get_remote_address()


limiter: Limiter = Limiter(
    key_func=_get_real_ip,
    storage_uri=_LIMITER_STORAGE_URI,
    default_limits=[],          # no global limit — only per-route
    headers_enabled=True,       # expose X-RateLimit-* headers to clients
)
