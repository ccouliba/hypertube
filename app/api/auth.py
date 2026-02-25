from flask import(
    Blueprint,
    request,
    jsonify,
    Response
)
from app.services import AuthService
from app.api.decorators.require_json import require_json

auth_bp: Blueprint = Blueprint("auth", __name__)
auth_service: AuthService = AuthService()


@auth_bp.route("/register", methods=["POST"])
@require_json
def register() -> tuple[Response, int]:
    """
    Register a new user
    ---
    POST /api/auth/register
    """
    data = request.get_json()
    result: dict = auth_service.register_user(data)
    return jsonify(result), 201


@auth_bp.route("/login", methods=["POST"])
@require_json
def login() -> tuple[Response, int]:
    """
    User login
    ---
    POST /api/auth/login
    """
    data = request.get_json()
    result: dict = auth_service.authenticate_user(data)
    return jsonify(result), 200


@auth_bp.route("/users", methods=["GET"])
def get_users() -> tuple[Response, int]:
    """
    Get the list of users
    ---
    GET /api/auth/users
    """
    users: list[dict] = auth_service.get_all_users()
    return jsonify({"users": users}), 200


@auth_bp.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id: int) -> tuple[Response, int]:
    """
    Get a user by ID
    ---
    GET /api/auth/users/{user_id}
    """
    user_data: dict = auth_service.get_user_by_id(
        user_id,
        request.host_url.rstrip('/')
    )
    return jsonify(user_data), 200


@auth_bp.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id: int) -> tuple[Response, int]:
    """
    Delete a user by ID
    ---
    DELETE /api/auth/users/{user_id}
    """
    result: dict = auth_service.delete_user_by_id(user_id)
    return jsonify(result), 200


@auth_bp.route("/users/<int:user_id>", methods=["PATCH"])
@require_json
def update_user(user_id: int) -> tuple[Response, int]:
    """
    Update a user's information
    ---
    PATCH /api/auth/users/{user_id}
    """
    data = request.get_json()
    result: dict = auth_service.update_user_by_id(user_id, data)
    return jsonify(result), 200
