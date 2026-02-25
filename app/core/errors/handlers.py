from werkzeug.exceptions import HTTPException
from flask import (jsonify, Response)

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
    500: "Internal Server Error"
}


class APIError(HTTPException):
    """Custom API Error Exception"""

    def __init__(self, status_code: int=400, message: str=None):
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
    """Handler global pour les APIError"""
    response: Response = jsonify(error.to_dict())
    response.status_code = error.code
    return response
