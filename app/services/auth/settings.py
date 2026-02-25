"""Authentication service settings"""
from app.core.configs.general import G_CONFIG as app_config
from app.core.configs.auth import AUTH_CONFIG as auth_config

auth_settings: dict[str, any] = {
    """Auth service settings dictionary"""

    "APP_URL": app_config["app"]["url"],
    "SECRET_KEY": auth_config["jwt"]["secret_key"],
    "ALGORITHM": auth_config["jwt"]["algorithm"],
    "EXPIRATION_DAYS": int(auth_config["jwt"]["expiration_days"]),
    "PASSWORD_MIN_LENGTH": int(auth_config["password"]["min_length"]),
    "PASSWORD_REQUIRE_UPP": bool(auth_config["password"]["require_uppercase"]),
    "PASSWORD_REQUIRE_LOW": bool(auth_config["password"]["require_lowercase"]),
    "PASSWORD_REQUIRE_DIGIT": bool(auth_config["password"]["require_digit"]),
    "PASSWORD_REQUIRE_LETTER": bool(auth_config["password"]["require_letter"]),
    "PASSWORD_REQUIRE_SPECIAL": bool(auth_config["password"]["require_special"]),
    "PASSWORD_SPECIALS_CHARS_PATTERN": auth_config["password"]["special_characters"],
    "USERNAME_MIN_LENGTH": int(auth_config["username"]["min_length"]),
    "USERNAME_MAX_LENGTH": int(auth_config["username"]["max_length"]),
    "USERNAME_AUTHORIZED_CHARS_PATTERN": auth_config["username"]["authorized_characters"],
    "SUPPORTED_LANGUAGES": list[str](auth_config["supported_languages"]),
    "EMAIL_PATTERN": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
}

