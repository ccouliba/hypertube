import pytest
import json
import base64
from app.core.errors.handlers import APIError
from app.services.auth.models import User


class TestAuthServiceRegister:

    def test_register_success(self, auth_service, user_data, db_session):
        result = auth_service.register_user(user_data)
        assert result["message"] == "User registered successfully"
        assert result["user"]["username"] == user_data["username"]
        user = db_session.query(User).filter_by(username=user_data["username"]).first()
        assert user is not None
        assert user.email == user_data["email"]

    def test_register_duplicate_username(self, auth_service, test_user, user_data):
        data = user_data.copy()
        data["username"] = test_user.username
        data["email"] = "different@example.com"
        with pytest.raises(APIError) as exc:
            auth_service.register_user(data)
        assert exc.value.code == 409

    def test_register_duplicate_email(self, auth_service, test_user, user_data):
        data = user_data.copy()
        data["username"] = "unique_user"
        data["email"] = test_user.email
        with pytest.raises(APIError) as exc:
            auth_service.register_user(data)
        assert exc.value.code == 409


class TestAuthServiceAuthenticate:

    def test_auth_success(self, auth_service, test_user, user_data):
        result = auth_service.authenticate_user({
            "username": test_user.username,
            "password": user_data["password"],
        })
        assert result["message"] == "Login successful"
        assert "access_token" in result
        assert "raw_refresh_token" in result
        assert result["user"]["id"] == test_user.id

    def test_auth_invalid_username(self, auth_service):
        with pytest.raises(APIError) as exc:
            auth_service.authenticate_user({
                "username": "nonexistent",
                "password": "Pass123!",
            })
        assert exc.value.code == 401

    def test_auth_invalid_password(self, auth_service, test_user, user_data):
        with pytest.raises(APIError) as exc:
            auth_service.authenticate_user({
                "username": test_user.username,
                "password": "WrongPass123!",
            })
        assert exc.value.code == 401


class TestAuthServiceGetUsers:

    def test_get_user_by_id_success(self, auth_service, test_user):
        result = auth_service.get_user_by_id(test_user.id, base_url="http://localhost:5000")
        assert result["username"] == test_user.username
        assert result["email"] == test_user.email

    def test_get_user_by_id_not_found(self, auth_service):
        with pytest.raises(APIError) as exc:
            auth_service.get_user_by_id(9999, base_url="http://localhost:5000")
        assert exc.value.code == 404


class TestAuthServiceDeleteUser:

    def test_delete_success(self, auth_service, db_session, user_data):
        auth_service.register_user(user_data)
        user = db_session.query(User).filter_by(username=user_data["username"]).first()
        result = auth_service.delete_user_by_id(user.id)
        assert result["message"] == "User deleted successfully"
        assert db_session.query(User).filter_by(id=user.id).first() is None

    def test_delete_not_found(self, auth_service):
        with pytest.raises(APIError) as exc:
            auth_service.delete_user_by_id(9999)
        assert exc.value.code == 404


class TestAuthServiceJWTToken:

    def test_jwt_generation(self, auth_service, test_user):
        token = auth_service.generate_jwt_token(test_user)
        assert token is not None
        assert isinstance(token, str)
        assert len(token.split(".")) == 3

    def test_jwt_contains_user_id(self, auth_service, test_user):
        token = auth_service.generate_jwt_token(test_user)
        payload_encoded = token.split(".")[1]
        padding = 4 - len(payload_encoded) % 4
        if padding != 4:
            payload_encoded += "=" * padding
        payload = json.loads(base64.urlsafe_b64decode(payload_encoded))
        assert payload["user_id"] == test_user.id

    def test_jwt_different_for_different_users(self, auth_service, db_session, user_data):
        auth_service.register_user(user_data)
        user2_data = user_data.copy()
        user2_data["username"] = "seconduser"
        user2_data["email"] = "second@example.com"
        auth_service.register_user(user2_data)
        user1 = db_session.query(User).filter_by(username=user_data["username"]).first()
        user2 = db_session.query(User).filter_by(username="seconduser").first()
        token1 = auth_service.generate_jwt_token(user1)
        token2 = auth_service.generate_jwt_token(user2)
        assert token1 != token2
