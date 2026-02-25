"""Auth service configurations"""
import os

AUTH_CONFIG: dict[str, any] = {
    "jwt": {
        "secret_key": os.getenv(
            "JWT_SECRET_KEY",
            "your-secret-key-change-in-production"
        ),
        "algorithm": "HS256",
        "expiration_days": int(os.getenv("JWT_EXPIRATION_DAYS", "7")),
    },
    "oauth": {
        "google_client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
        "google_client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
        "github_client_id": os.getenv("GITHUB_CLIENT_ID", ""),
        "github_client_secret": os.getenv("GITHUB_CLIENT_SECRET", ""),
        "42_client_id": os.getenv("INTRA_42_CLIENT_ID", ""),
        "42_client_secret": os.getenv("INTRA_42_CLIENT_SECRET", ""),
    },
    "username": {
        "min_length": int(os.getenv("USERNAME_MIN_LENGTH", "2")),
        "max_length": int(os.getenv("USERNAME_MAX_LENGTH", "20")),
        "authorized_characters": os.getenv("USERNAME_AUTHORIZED_CHARACTERS", r'^[a-zA-Z0-9_-]+$'),
    },
    "password": {
        "min_length": int(os.getenv("PASSWORD_MIN_LENGTH", "6")),
        "require_uppercase": os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true",
        "require_lowercase": os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true",
        "require_digit": os.getenv("PASSWORD_REQUIRE_DIGIT", "true").lower() == "true",
        "require_letter": os.getenv("PASSWORD_REQUIRE_LETTER", "true").lower() == "true",
        "require_special": os.getenv("PASSWORD_REQUIRE_SPECIAL", "false").lower() == "true",
        "special_characters": os.getenv("SPECIAL_CHARACTERS", r'[!@#$%^&*(),.?":{}|<>]'),
    },
    "session": {
        "timeout_minutes": int(os.getenv("SESSION_TIMEOUT_MINUTES", "120")),
    },
    "supported_languages": os.getenv("SUPPORTED_LANGUAGES", "en,fr,es,de,it,pt").split(","),
}
