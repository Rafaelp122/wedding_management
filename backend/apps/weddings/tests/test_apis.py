from datetime import timedelta

import pytest
from django.utils import timezone

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingNinjaAPI:
    def test_list_weddings_isolation(self, auth_client, user):
        WeddingFactory(company=user.company, bride_name="Noiva do User")
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
        assert Wedding.objects.filter(company=user.company).count() == 1

    def test_create_wedding_with_past_date_returns_422(self, auth_client):
        payload = {
            "groom_name": "Noivo",
            "bride_name": "Noiva",
            "date": (timezone.now().date() - timedelta(days=1)).isoformat(),
            "location": "Salão Teste",
            "expected_guests": 100,
            "total_estimated": "10000.00",
        }

        response = auth_client.post(
            "/api/v1/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "wedding_validation_error"
        assert "A data do casamento não pode ser no passado." in body["detail"]

    def test_unauthenticated_access_denied(self, client):
        response = client.get("/api/v1/weddings/")
        assert response.status_code == 401

    def test_list_weddings_filter_by_search(self, auth_client, user):
        WeddingFactory(
            company=user.company,
            bride_name="Maria",
            groom_name="João",
            location="Praia",
        )
        WeddingFactory(
            company=user.company,
            bride_name="Ana",
            groom_name="Carlos",
            location="Igreja",
        )

        response = auth_client.get("/api/v1/weddings/?search=maria")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["bride_name"] == "Maria"

    def test_list_weddings_filter_by_status(self, auth_client, user):
        from apps.weddings.models import Wedding

        WeddingFactory(
            company=user.company,
            bride_name="Ativa",
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        WeddingFactory(
            company=user.company,
            bride_name="Cancelada",
            status=Wedding.StatusChoices.CANCELED,
        )

        response = auth_client.get("/api/v1/weddings/?status=CANCELED")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["bride_name"] == "Cancelada"

    def test_list_weddings_filter_by_search_and_status(self, auth_client, user):
        from apps.weddings.models import Wedding

        WeddingFactory(
            company=user.company,
            bride_name="Maria A",
            groom_name="João",
            status=Wedding.StatusChoices.IN_PROGRESS,
        )
        WeddingFactory(
            company=user.company,
            bride_name="Maria B",
            groom_name="Pedro",
            status=Wedding.StatusChoices.CANCELED,
        )

        response = auth_client.get("/api/v1/weddings/?search=maria&status=CANCELED")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["bride_name"] == "Maria B"
