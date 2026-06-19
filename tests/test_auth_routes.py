import pytest
from flask import json as flask_json


class TestAuthRoutesRegister:

    def test_register_success(self, client, user_data):
        response = client.post("/api/auth/register", json=user_data, content_type="application/json")
        assert response.status_code == 201
        data = response.get_json()
        assert data["message"] == "User registered successfully"
        assert data["user"]["username"] == user_data["username"]

    def test_register_duplicate_username(self, client, test_user, user_data):
        duplicate = user_data.copy()
        duplicate["username"] = test_user.username
        duplicate["email"] = "different@example.com"
        response = client.post("/api/auth/register", json=duplicate, content_type="application/json")
        assert response.status_code == 409

    def test_register_duplicate_email(self, client, test_user, user_data):
        duplicate = user_data.copy()
        duplicate["username"] = "newusername"
        duplicate["email"] = test_user.email
        response = client.post("/api/auth/register", json=duplicate, content_type="application/json")
        assert response.status_code == 409

    @pytest.mark.parametrize("field,value", [
        ("firstname", ""), ("lastname", ""), ("username", ""),
        ("email", ""), ("password", ""), ("email", "invalid-email"),
    ])
    def test_register_invalid_data(self, client, user_data, field, value):
        invalid_data = user_data.copy()
        invalid_data[field] = value
        response = client.post("/api/auth/register", json=invalid_data, content_type="application/json")
        assert response.status_code in [400, 422]


class TestAuthRoutesLogin:

    def test_login_success(self, client, test_user):
        response = client.post(
            "/api/auth/login",
            json={"username": test_user.username, "password": test_user._test_password},
            content_type="application/json"
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "Login successful"
        assert "access_token" in data
        assert data["user"]["username"] == test_user.username
        assert data["user"]["email"] == test_user.email

    def test_login_invalid_username(self, client):
        response = client.post(
            "/api/auth/login",
            json={"username": "nonexistent", "password": "Pass123!"},
            content_type="application/json"
        )
        assert response.status_code == 401

    def test_login_invalid_password(self, client, user_data):
        response = client.post(
            "/api/auth/login",
            json={"username": user_data["username"], "password": "Wrong123!"},
            content_type="application/json"
        )
        assert response.status_code == 401

    @pytest.mark.parametrize("username,password", [
        ("", ""), ("user", ""), ("", "password"),
    ])
    def test_login_empty_credentials(self, client, username, password):
        response = client.post(
            "/api/auth/login",
            json={"username": username, "password": password},
            content_type="application/json"
        )
        assert response.status_code in [400, 401, 422]


class TestAuthRoutesGetUsers:

    # def test_get_all_users_success(self, client, auth_headers):
    #     response = client.get("/api/auth/users", headers=auth_headers)
    #     assert response.status_code == 200
    #     data = response.get_json()
    #     assert "users" in data or isinstance(data, list)

    # def test_get_all_users_without_auth(self, client):
    #     response = client.get("/api/auth/users")
    #     assert response.status_code == 401

    def test_get_user_by_id_success(self, client, test_user, auth_headers):
        response = client.get(f"/api/auth/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["username"] == test_user.username

    def test_get_user_by_id_not_found(self, client, auth_headers):
        response = client.get("/api/auth/users/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_get_user_by_id_without_auth(self, client, test_user):
        response = client.get(f"/api/auth/users/{test_user.id}")
        assert response.status_code == 401


class TestAuthRoutesDeleteUser:

    def test_delete_user_success(self, client, test_user, auth_headers):
        response = client.delete(f"/api/auth/users/{test_user.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert data["message"] == "User deleted successfully"

    def test_delete_user_not_found(self, client, auth_headers):
        response = client.delete("/api/auth/users/9999", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_user_without_auth(self, client, test_user):
        response = client.delete(f"/api/auth/users/{test_user.id}")
        assert response.status_code == 401
