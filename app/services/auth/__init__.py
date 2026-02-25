"""Auth module - Authentication and authorization

Provides:
- User authentication (register, login, token refresh)
- JWT token management
- Auth decorators for protected endpoints
- User models and validators
"""
from services.auth.dao import UserDAO
from services.auth.models import User
from services.auth.service import AuthService
from services.auth.validators import UserValidator
from services.auth.settings import auth_settings

__all__ = [
    "User",
    "UserDAO",
    "AuthService",
    "UserValidator",
    "auth_settings",
]
