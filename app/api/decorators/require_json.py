"""Require JSON content-type decorators"""
from flask import request
from functools import wraps
from app.core.errors import APIError
from app.core.configs.general import G_CONFIG as app_config

CONTENT_TYPE: str = app_config["app"]["content_type"]


def require_json(f):
    """Decorator to ensure request Content-Type is application/json"""
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.content_type == CONTENT_TYPE:
            raise APIError(status_code=415)
        return f(*args, **kwargs)
    return decorated_function
