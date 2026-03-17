import logging
from werkzeug.exceptions import HTTPException
from flask import (jsonify, Response)

LOGGER: logging.Logger = logging.getLogger(__name__)

ERRORS: dict[int, str] = {
    # 4xx -> Client Errors
    400: "Bad Request",
    401: "Unauthorized - Invalid credentials",
    403: "Forbidden",
    404: "Resource not found",
    409: "Conflict - Resource already exists",
    415: "Unsupported Media Type",
    422: "Missing or invalid fields",
    # 5xx -> Server Errors
    500: "Internal Server Error",
    503: "Service Unavailable"
}


class APIError(HTTPException):
    """Custom HTTP error raised anywhere in the application and handled globally."""

    def __init__(
        self,
        status_code: int = 400,
        message: str | None = None
    ) -> None:
        self.message: str = message or ERRORS.get(
            status_code,
            "An error occurred"
        )
        super().__init__(description=self.message)
        self.code: int = status_code

    def to_dict(self) -> dict:
        return {
            "error": self.message,
            "status_code": self.code
        }


def handle_api_error(error: APIError) -> Response:
    """Global error handler — serialises APIError to a JSON response."""
    response: Response = jsonify(error.to_dict())
    response.status_code = error.code
    return response


def handle_http_exception(error: HTTPException) -> Response:
    """Catch Werkzeug native HTTP errors (404, 405, 429…) and return uniform JSON."""
    status_code: int = error.code or 500
    message: str = ERRORS.get(status_code, error.description or "An error occurred")
    response: Response = jsonify({"error": message, "status_code": status_code})
    response.status_code = status_code
    return response


def handle_unhandled_exception(error: Exception) -> Response:
    """Last-resort catch-all — logs the full traceback and returns a generic 500 JSON."""
    LOGGER.exception("Unhandled exception: %s", error)
    response: Response = jsonify({"error": ERRORS[500], "status_code": 500})
    response.status_code = 500
    return response
