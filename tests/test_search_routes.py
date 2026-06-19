import pytest


class TestSearchRoutesAuth:

    def test_search_without_auth(self, client):
        response = client.get("/api/search/?query=test&page=1&limit=10")
        assert response.status_code == 401

    def test_search_invalid_token(self, client, invalid_auth_headers):
        response = client.get("/api/search/?query=test&page=1&limit=10", headers=invalid_auth_headers)
        assert response.status_code == 401

    def test_search_valid_token(self, client, auth_headers):
        response = client.get("/api/search/?query=test&page=1&limit=10", headers=auth_headers)
        assert response.status_code in [200, 400]


class TestSearchRoutesPopular:

    def test_popular_no_query(self, client, auth_headers):
        response = client.get("/api/search/?page=1&limit=10", headers=auth_headers)
        assert response.status_code == 200
        data = response.get_json()
        assert any(key in data for key in ["movies", "tv_shows", "results"])

    def test_popular_custom_limit(self, client, auth_headers):
        response = client.get("/api/search/?page=1&limit=20", headers=auth_headers)
        assert response.status_code == 200


class TestSearchRoutesQueries:

    @pytest.mark.parametrize("query", [
        "Breaking Bad", "Game of Thrones", "Inception", "The Matrix",
    ])
    def test_search_queries(self, client, auth_headers, query):
        response = client.get(f"/api/search/?query={query}&page=1&limit=10", headers=auth_headers)
        assert response.status_code == 200

    def test_search_empty_results(self, client, auth_headers):
        response = client.get("/api/search/?query=zzzzzzzzzzz&page=1&limit=10", headers=auth_headers)
        assert response.status_code == 200

    def test_search_special_chars(self, client, auth_headers):
        response = client.get("/api/search/?query=C++&page=1&limit=10", headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_search_unicode(self, client, auth_headers):
        response = client.get("/api/search/?query=Amelie&page=1&limit=10", headers=auth_headers)
        assert response.status_code == 200


class TestSearchRoutesPagination:

    @pytest.mark.parametrize("page,limit", [
        (1, 10), (1, 20), (2, 10), (1, 50),
    ])
    def test_pagination_valid(self, client, auth_headers, page, limit):
        response = client.get(f"/api/search/?query=test&page={page}&limit={limit}", headers=auth_headers)
        assert response.status_code == 200

    @pytest.mark.parametrize("page,limit", [
        (0, 10), (1, 0), (-1, 10), (1, -10),
    ])
    def test_pagination_invalid(self, client, auth_headers, page, limit):
        response = client.get(f"/api/search/?query=test&page={page}&limit={limit}", headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_pagination_missing_page(self, client, auth_headers):
        response = client.get("/api/search/?query=test&limit=10", headers=auth_headers)
        assert response.status_code == 200

    def test_pagination_missing_limit(self, client, auth_headers):
        response = client.get("/api/search/?query=test&page=1", headers=auth_headers)
        assert response.status_code == 200


class TestSearchRoutesSecurity:

    def test_sql_injection_attempt(self, client, auth_headers):
        response = client.get("/api/search/?query='; DROP TABLE videos; --&page=1", headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_xss_attempt(self, client, auth_headers):
        response = client.get("/api/search/?query=<script>alert('xss')</script>&page=1", headers=auth_headers)
        assert response.status_code in [200, 400]

    def test_long_query(self, client, auth_headers):
        long_query = "a" * 1000
        response = client.get(f"/api/search/?query={long_query}&page=1", headers=auth_headers)
        assert response.status_code in [200, 400, 414]
