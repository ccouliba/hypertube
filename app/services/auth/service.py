import jwt
from typing import Any
from datetime import (datetime, timedelta)
from app.core.errors.handlers import APIError
from app.core.errors.messages import ERROR_MESSAGES
from app.services.auth.models import User
from app.services.auth.dao import UserDAO
from app.services.auth.settings import auth_settings as settings    
from app.services.auth.validators import UserValidator

class AuthService:
    """Service for authentication and user management"""
    
    def __init__(self):
        self.user_dao: UserDAO = UserDAO()
        self.validator: UserValidator = UserValidator()
    
    def register_user(
            self,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Register a new user
        Args:
            data: Registration data
        Returns:
            Success message with user info
        Raises:
            APIError: If username or email already exists
        """
        validated_data: dict = self.validator.validate_registration(data)
        if self.user_dao.exists_by_username(validated_data["username"]):
            raise APIError(
                status_code=409, 
                message=ERROR_MESSAGES["USERNAME_EXISTS"]
            )
        if self.user_dao.exists_by_email(validated_data["email"]):
            raise APIError(
                status_code=409,
                message=ERROR_MESSAGES["EMAIL_EXISTS"]
            )
        user: User = self.user_dao.create(**validated_data)
        return {
            "message": "User registered successfully",
            "user": {
                "username": user.username,
                "profile_picture": user.profile_picture,
            }
        }

    def authenticate_user(
            self,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Authenticate a user
        Args:
            data: Login credentials
        Returns:
            Success message with user info and JWT token
        Raises:
            APIError: If credentials are invalid
        """
        credentials: dict = self.validator.validate_login(data)
        user: User = self.user_dao.authenticate(**credentials)
        if not user:
            raise APIError(
                status_code=401,
                message=ERROR_MESSAGES["INVALID_CREDENTIALS"]
            )
        token: str = self.generate_jwt_token(user)
        return {
            "message": "Login successful",
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "profile_picture": user.profile_picture,
            }
        }

    def get_all_users(self) -> list[dict[str, Any]]:
        """Get all users"""
        users: list[User] = self.user_dao.get_all()
        return [
            {
                "id": user.id,
                "username": user.username,
            }
            for user in users
        ]

    def get_user_by_id(
            self, user_id: int,
            base_url: str
        ) -> dict[str, Any]:
        """
        Get a user by ID
        Args:
            user_id: User ID
            base_url: Base URL for profile picture
        Returns:
            User data
        Raises:
            APIError: If user not found
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        return {
            "username": user.username,
            "email": user.email,
            "firstname": user.firstname,
            "lastname": user.lastname,
            "language": user.language,
            # "created_at": user.created_at.isoformat() if user.created_at else None,
            "profile_picture": user.get_profile_picture_url(base_url=base_url),
        }

    def delete_user_by_id(self, user_id: int) -> dict[str, str]:
        """
        Delete a user by ID
        Args:
            user_id: User ID
        Returns:
            Success message
        Raises:
            APIError: If user not found
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        self.user_dao.delete(user)
        return {"message": "User deleted successfully"}

    def update_user_by_id(
            self,
            user_id: int,
            data: dict[str, Any]
        ) -> dict[str, Any]:
        """
        Update a user's information
        Args:
            user_id: User ID
            data: Update data
        Returns:
            Success message with updated user info
        Raises:
            APIError: If user not found or validation fails
        """
        user: User = self.user_dao.get_by_id(user_id)
        if not user:
            raise APIError(
                status_code=404,
                message=ERROR_MESSAGES["USER_NOT_FOUND"]
            )
        validated_data: dict = self.validator.validate_update(data)
        if "username" in validated_data and validated_data["username"] != user.username:
            if self.user_dao.exists_by_username(validated_data["username"]):
                raise APIError(
                    status_code=409,
                    message=ERROR_MESSAGES["USERNAME_EXISTS"]
                )
        if "email" in validated_data and validated_data["email"] != user.email:
            if self.user_dao.exists_by_email(validated_data["email"]):
                raise APIError(
                    status_code=409,
                    message=ERROR_MESSAGES["EMAIL_EXISTS"]
                )
        if "language" in validated_data and validated_data["language"] != user.language:
            if validated_data["language"] not in settings.get("SUPPORTED_LANGUAGES", []):
                raise APIError(
                    status_code=400,
                    message=ERROR_MESSAGES["UNSUPPORTED_LANGUAGE"]
                )

        for field, value in validated_data.items():
            setattr(user, field, value)

        self.user_dao.update(user)
        
        return {
            "message": "User updated successfully",
            "user": {
                "firstname": user.firstname,
                "lastname": user.lastname,
                "username": user.username,
                "email": user.email,
                "language": user.language,
                "profile_picture": user.profile_picture,

            }
        }
    
    def generate_jwt_token(self, user: User) -> str:
        """
        Generate JWT token for authenticated user
        Args:
            user: Authenticated user
        Returns:
            JWT token string
        """
        secret_key: str = settings.get("SECRET_KEY", "default_secret")
        expiration = datetime.utcnow() + timedelta(days=settings.get("EXPIRATION_DAYS", 7))
        payload = {
            "user_id": user.id,
            "username": user.username,
            "exp": expiration
        }
        return jwt.encode(payload, secret_key, algorithm=settings.get("ALGORITHM", "HS256"))
