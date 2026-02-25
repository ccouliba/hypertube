"""Auth domain validators"""
import re
from typing import Any
from app.core.bases.validator import BaseValidator
from app.core.errors import (APIError, ERROR_MESSAGES)
from app.services.auth.settings import auth_settings as settings


class UserValidator(BaseValidator):
    """Validator for User-related operations"""
    
    @staticmethod
    def validate_password(password: str) -> None:
        """Validate password strength (min 8 chars, letter + number)"""
        if not password or len(password) < settings.get("PASSWORD_MIN_LENGTH", 8):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["PASSWORD_TOO_SHORT"]
            )
        if settings.get("PASSWORD_REQUIRE_LETTER", True) and not re.search(r'[A-Za-z]', password):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["PASSWORD_NO_LETTER"]
            )
        # if _PASSWORD_REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
        #     raise APIError(
        #         status_code=400,
        #         message=ERROR_MESSAGES["PASSWORD_NO_UPPERCASE"]
        #     )
        # if _PASSWORD_REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
        #     raise APIError(
        #         status_code=400,
        #         message=ERROR_MESSAGES["PASSWORD_NO_LOWERCASE"]
        #     )
        if settings.get("PASSWORD_REQUIRE_DIGIT", True) and not re.search(r'\d', password):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["PASSWORD_NO_NUMBER"]
            )
        if settings.get("PASSWORD_REQUIRE_SPECIAL", True) and not re.search(settings.get("PASSWORD_SPECIALS_CHARS_PATTERN", r'[!@#$%^&*(),.?":{}|<>]'), password):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["PASSWORD_NO_SPECIAL"]
            )
    
    @staticmethod
    def validate_registration(
        data: dict[str, Any]
    ) -> dict[str, str]:
        """
        Validate user registration data
        Returns cleaned data ready for UserDAO.create()
        """
        UserValidator.validate_required_fields(
            data,
            ["firstname", "lastname", "username", "email", "password"]
        )
        firstname: str = data["firstname"].strip()
        lastname: str = data["lastname"].strip()
        username: str = data["username"].strip()
        email: str = data["email"].strip().lower()
        password: str = data["password"]
        UserValidator.validate_names(firstname, lastname)
        UserValidator.validate_username(username)
        UserValidator.validate_email(email)
        UserValidator.validate_password(password)
        return {
            "firstname": firstname,
            "lastname": lastname,
            "username": username,
            "email": email,
            "password": password
        }
    
    @staticmethod
    def validate_login(data: dict[str, Any]) -> dict[str, str]:
        """
        Validate login credentials
        Returns cleaned data ready for UserDAO.authenticate()
        """
        UserValidator.validate_required_fields(
            data, 
            ["username", "password"]
        )
        username: str = data["username"].strip()
        password: str = data["password"]
        return {"username": username, "password": password}
    
    @staticmethod
    def validate_update(data: dict[str, Any]) -> dict[str, str]:
        """
        Validate user update data (partial update)
        Returns only validated fields that were provided
        """
        validated = {}
        for field in ["firstname", "lastname", "username", "email", "language", "profile_picture"]:
            if field not in data:
                continue
            value = data[field].strip() if isinstance(data[field], str) else ""
            if not value:
                continue
            match field:
                case "firstname" | "lastname":
                    UserValidator.validate_string_length(
                        value,
                        field.capitalize(), 1, 80
                    )
                    validated[field] = value
                case "username":
                    UserValidator.validate_username(value)
                    validated[field] = value
                case "email":
                    value = value.lower()
                    UserValidator.validate_email(value)
                    validated[field] = value
                case "language":
                    UserValidator.validate_language(value)
                    validated[field] = value
                case "profile_picture":
                    validated[field] = value
        return validated

    @staticmethod
    def validate_names(firstname: str, lastname: str) -> None:
        """Validate firstname and lastname"""
        UserValidator.validate_string_length(
            firstname,
            "Firstname",
            min_len=settings.get("USERNAME_MIN_LENGTH", 2),
        )
        UserValidator.validate_string_length(
            lastname,
            "Lastname",
            min_len=settings.get("USERNAME_MIN_LENGTH", 2),
        )
    
    @staticmethod
    def validate_username(username: str) -> None:
        """Validate username format (2-20 chars, alphanumeric + _ -)"""
        username = username.strip() if username else ""
        if not username:
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["USERNAME_REQUIRED"]
            )
        UserValidator.validate_string_length(
            username,
            "Username",
            settings.get("USERNAME_MIN_LENGTH", 2),
            settings.get("USERNAME_MAX_LENGTH", 20)
        )
        if not re.match(settings.get("USERNAME_AUTHORIZED_CHARS_PATTERN", r'^[a-zA-Z0-9_-]+$'), username):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["USERNAME_INVALID_CHARS"]
            )

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email format"""
        if not email or not email.strip():
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["EMAIL_REQUIRED"]
            )
        email_pattern = settings["EMAIL_PATTERN"]
        if not re.match(email_pattern, email.strip()):
            raise APIError(
                status_code=400,
                message=ERROR_MESSAGES["INVALID_EMAIL"]
            )
    