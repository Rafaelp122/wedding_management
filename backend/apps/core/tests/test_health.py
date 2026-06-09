import pytest
from django.test import Client


@pytest.mark.django_db
class TestHealthCheck:
    def test_health_check_healthy(self, client: Client):
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["database"] == "up"

    def test_health_check_requires_no_auth(self, client: Client):
        response = client.get("/api/v1/health")
        assert response.status_code != 401
        assert response.status_code != 403
