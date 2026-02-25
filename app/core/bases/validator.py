"""
Base Validator - Abstract class for all validators
"""
import re
from abc import ABC
from typing import Any
from app.core.errors import (APIError, ERROR_MESSAGES)


class BaseValidator(ABC):
    """
    Abstract base class for all validators
    Each DAO should have its own validator
    """
    def validate_required_chars(
        self,
        value: str,
        pattern: str,
        error_message: str
    ) -> None:
        """Validate that a string contains only allowed characters"""
        if not re.match(pattern, value):
            raise APIError(
                status_code=400,
                message=error_message
            )

    @staticmethod
    def validate_required_fields(
        data: dict[str, Any],
        fields: list
    ) -> None:
        """Check if required fields are present and not empty"""
        missing = []
        for field in fields:
            value = data.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        if missing:
            raise APIError(
                status_code=422,
                message=f"{ERROR_MESSAGES['MISSING_FIELDS']}: {', '.join(missing)}"
            )
    
    @staticmethod
    def validate_string_length(
        value: str,
        field_name: str,
        min_len: int = 1,
        max_len: int = 80
    ) -> None:
        """Validate string length"""
        value = value.strip() if value else ""
        if not value:
            raise APIError(
                status_code=400,
                message=f"{field_name} is required"
            )
        if len(value) < min_len:
            raise APIError(
                status_code=400,
                message=f"{field_name} must be at least {min_len} characters"
            )
        if len(value) > max_len:
            raise APIError(
                status_code=400,
                message=f"{field_name} must be at most {max_len} characters"
            )
    
    @staticmethod
    def validate_integer_range(
        value: int,
        field_name: str,
        min_val: int,
        max_val: int = None
    ) -> None:
        """Validate integer is within range"""
        if not isinstance(value, int):
            raise APIError(
                status_code=400,
                message=f"{field_name} must be an integer"
            )
        if value < min_val:
            raise APIError(
                status_code=400,
                message=f"{field_name} must be at least {min_val}"
            )
        if max_val and value > max_val:
            raise APIError(
                status_code=400,
                message=f"{field_name} must be at most {max_val}"
            )
    
    @staticmethod
    def validate_language(language: str) -> None:
        """Validate language code - only checks if it's supported"""
        SUPPORTED_LANGUAGES = ["en", "fr"]
        if language.strip().lower() not in SUPPORTED_LANGUAGES:
            raise APIError(
                status_code=400,
                message=f"Unsupported language. Supported: {', '.join(SUPPORTED_LANGUAGES)}"
            )
