import pytest


class TestVideoRoutesAuth:

    def test_get_without_auth(self, client):
        response = client.get("/api/video/")
        assert response.status_code == 401

    def test_get_invalid_token(self, client, invalid_auth_headers):
        response = client.get("/api/video/", headers=invalid_auth_headers)
        assert response.status_code == 401

    def test_get_valid_auth(self, client, auth_headers):
        response = client.get("/api/video/", headers=auth_headers)
        assert response.status_code == 200


class TestVideoRoutesGetAll:

    def test_all_empty(self, client, auth_headers):
        response = client.get("/api/video/?content_type=all", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["total"] == 0

    def test_returns_structure(self, client, auth_headers):
        response = client.get("/api/video/?content_type=all", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "videos" in data and "total" in data

    @pytest.mark.parametrize("content_type", ["all", "movie", "tv_show"])
    def test_filter_by_type(self, client, auth_headers, content_type):
        response = client.get(f"/api/video/?content_type={content_type}", headers=auth_headers)
        assert response.status_code == 200

    def test_default_type(self, client, auth_headers):
        response = client.get("/api/video/", headers=auth_headers)
        assert response.status_code == 200

    def test_invalid_type(self, client, auth_headers):
        response = client.get("/api/video/?content_type=invalid", headers=auth_headers)
        assert response.status_code in [400, 200]


class TestVideoRoutesGetById:

    def test_get_by_id(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.get(f"/api/video/{created.id}?content_type=movie", headers=auth_headers)
        assert response.status_code == 200
        assert response.get_json()["id"] == created.id

    def test_not_found(self, client, auth_headers):
        response = client.get("/api/video/9999?content_type=movie", headers=auth_headers)
        assert response.status_code == 404

    def test_missing_content_type(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.get(f"/api/video/{created.id}", headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_without_auth(self, client, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.get(f"/api/video/{created.id}?content_type=movie")
        assert response.status_code == 401

    @pytest.mark.parametrize("video_id", [0, -1, 99999, "invalid"])
    def test_invalid_ids(self, client, auth_headers, video_id):
        response = client.get(f"/api/video/{video_id}?content_type=movie", headers=auth_headers)
        assert response.status_code in [400, 404]


class TestVideoRoutesUpdate:

    def test_update_success(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.patch(
            f"/api/video/{created.id}?content_type=movie",
            json={"rating": 9.5},
            headers=auth_headers,
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_update_status(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.patch(
            f"/api/video/{created.id}?content_type=movie",
            json={"download_status": "downloading"},
            headers=auth_headers,
            content_type="application/json"
        )
        assert response.status_code == 200

    def test_update_not_found(self, client, auth_headers):
        response = client.patch(
            "/api/video/9999?content_type=movie",
            json={"rating": 9.0},
            headers=auth_headers,
            content_type="application/json"
        )
        assert response.status_code == 404

    def test_update_without_auth(self, client, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.patch(
            f"/api/video/{created.id}?content_type=movie",
            json={"rating": 9.0},
            content_type="application/json"
        )
        assert response.status_code == 401

    @pytest.mark.parametrize("field,value", [
        ("rating", 9.5), ("download_progress", 50), ("download_status", "downloading"),
    ])
    def test_update_fields(self, client, auth_headers, movie_service, movie_data, field, value):
        created = movie_service.dao.create(**movie_data)
        response = client.patch(
            f"/api/video/{created.id}?content_type=movie",
            json={field: value},
            headers=auth_headers,
            content_type="application/json"
        )
        assert response.status_code == 200


class TestVideoRoutesDelete:

    def test_delete_success(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.delete(f"/api/video/{created.id}?content_type=movie", headers=auth_headers)
        assert response.status_code == 200

    def test_delete_not_found(self, client, auth_headers):
        response = client.delete("/api/video/9999?content_type=movie", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_without_auth(self, client, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.delete(f"/api/video/{created.id}?content_type=movie")
        assert response.status_code == 401

    def test_delete_twice(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        video_id = created.id
        response1 = client.delete(f"/api/video/{video_id}?content_type=movie", headers=auth_headers)
        assert response1.status_code == 200
        response2 = client.delete(f"/api/video/{video_id}?content_type=movie", headers=auth_headers)
        assert response2.status_code == 404


class TestVideoRoutesResponseFormat:

    def test_list_format(self, client, auth_headers, movie_service, movie_data):
        movie_service.dao.create(**movie_data)
        response = client.get("/api/video/?content_type=movie", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data.get("videos"), list) and "total" in data

    def test_single_format(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.get(f"/api/video/{created.id}?content_type=movie", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert "id" in data and "title" in data

    def test_json_response(self, client, auth_headers):
        response = client.get("/api/video/?content_type=movie", headers=auth_headers)
        assert response.content_type.startswith("application/json")


class TestVideoRoutesEdgeCases:

    def test_special_chars(self, client, auth_headers):
        response = client.get("/api/video/?content_type=movie&search=test's", headers=auth_headers)
        assert response.status_code in [200, 400, 404]

    def test_large_id(self, client, auth_headers):
        response = client.get("/api/video/999999999?content_type=movie", headers=auth_headers)
        assert response.status_code == 404

    def test_update_empty_body(self, client, auth_headers, movie_service, movie_data):
        created = movie_service.dao.create(**movie_data)
        response = client.patch(
            f"/api/video/{created.id}?content_type=movie",
            json={},
            headers=auth_headers,
            content_type="application/json"
        )
        assert response.status_code in [200, 400]
