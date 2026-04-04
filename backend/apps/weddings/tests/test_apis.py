import pytest

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingNinjaAPI:
    def test_list_weddings_isolation(self, auth_client, user):
        WeddingFactory(planner=user, bride_name="Noiva do User")
        WeddingFactory(bride_name="Noiva Alheia")

        response = auth_client.get("/api/v1/weddings/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["bride_name"] == "Noiva do User"

    def test_retrieve_wedding_forbidden_for_other_planner(self, auth_client):
        other_wedding = WeddingFactory(bride_name="Noiva Secreta")

        response = auth_client.get(f"/api/v1/weddings/{other_wedding.uuid}/")

        assert response.status_code == 404

    def test_create_wedding_via_api_success(self, auth_client, user):
        payload = {
            "groom_name": "Rafael Ninja",
            "bride_name": "Noiva de Teste",
            "date": "2026-12-31",
            "location": "Espaço Alvorada",
            "expected_guests": 150,
            "total_estimated": "50000.00",
        }

        response = auth_client.post(
            "/api/v1/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 201
        data = response.json()
        assert "uuid" in data
        assert Wedding.objects.filter(planner=user).count() == 1

    def test_unauthenticated_access_denied(self, client):
        response = client.get("/api/v1/weddings/")
        assert response.status_code == 401
