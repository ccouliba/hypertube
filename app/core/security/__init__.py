"""Security - Application security package utilities

Provides:
- CORS definition utility
- JSON request requirement decorator
"""
from app.core.security.cors import define_CORS

__all__ = [
    "define_CORS",
]
