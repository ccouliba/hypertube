"""Errors module for core application

Provides:
- API error handling
- Standardized error messages
"""

from app.core.errors.handlers import APIError
from app.core.errors.messages import ERROR_MESSAGES
from app.core.errors.handlers import (
    handle_api_error,
    APIError
)

__all__ = [
    "APIError",
    "ERROR_MESSAGES",
    "handle_api_error",
]
