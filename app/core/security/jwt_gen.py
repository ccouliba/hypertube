"""JWT utility functions — centralized token generation and decoding"""
import os
import jwt
from datetime import datetime, timedelta, timezone


def generate_token(
    payload: dict,
    expiration: timedelta,
    secret: str,
    algorithm: str = "HS256",
) -> str:
    """
    Generate a signed JWT token.
    Args:
        payload: Claims to embed (user_id, username, ...)
        expiration: Token lifetime as timedelta
        secret: Signing secret
        algorithm: Signing algorithm (default HS256)
    Returns:
        Encoded JWT string
    """
    data: dict = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + expiration
    return jwt.encode(data, secret, algorithm=algorithm)


def decode_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    Args:
        token: Encoded JWT string
    Returns:
        Decoded payload dict
    Raises:
        RuntimeError: If JWT_SECRET_KEY env var is not set
        jwt.ExpiredSignatureError: If token is expired
        jwt.InvalidTokenError: If token is invalid
    """
    secret: str | None = os.getenv("JWT_SECRET_KEY")
    if not secret:
        raise RuntimeError("JWT_SECRET_KEY environment variable is not set")
    return jwt.decode(token, secret, algorithms=["HS256"])
