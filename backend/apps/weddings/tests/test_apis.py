from datetime import date, timedelta
from typing import Any, cast

import pytest
from django.utils import timezone

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


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

    def test_create_wedding_with_empty_bride_name_returns_422_schema_error(
        self, auth_client
    ):
        """Nível 1: Pydantic rejeita string vazia com 422
        validation_error na entrada.
        """
        payload = {
            "groom_name": "Noivo",
            "bride_name": "",
            "date": (timezone.now().date() + timedelta(days=30)).isoformat(),
            "location": "Salão Teste",
        }

        response = auth_client.post(
            "/api/v1/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "validation_error"

    def test_create_wedding_with_whitespace_only_bride_name_returns_422(
        self, auth_client
    ):
        """Nível 1: str_strip_whitespace=True sanitiza e rejeita apenas espaços."""
        payload = {
            "groom_name": "Noivo",
            "bride_name": "    ",
            "date": (timezone.now().date() + timedelta(days=30)).isoformat(),
            "location": "Salão Teste",
        }

        response = auth_client.post(
            "/api/v1/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "validation_error"

    def test_create_wedding_with_negative_guests_returns_422(self, auth_client):
        """Nível 1: expected_guests ge=1 rejeita valores negativos ou zero."""
        payload = {
            "groom_name": "Noivo",
            "bride_name": "Noiva",
            "date": (timezone.now().date() + timedelta(days=30)).isoformat(),
            "location": "Salão Teste",
            "expected_guests": -10,
        }

        response = auth_client.post(
            "/api/v1/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "validation_error"

    def test_update_wedding_with_empty_bride_name_returns_422(self, auth_client, user):
        """Nível 1: WeddingPatchIn rejeita bride_name vazio com 422 validation_error."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.patch(
            f"/api/v1/weddings/{wedding.uuid}/",
            data={"bride_name": ""},
            content_type="application/json",
        )

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "validation_error"

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

    def test_update_wedding_success(self, auth_client, user):
        """PATCH deve atualizar parcialmente um casamento."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.patch(
            f"/api/v1/weddings/{wedding.uuid}/",
            data={"location": "Praia do Forte"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["location"] == "Praia do Forte"

    def test_update_wedding_valid_status_success(self, auth_client, user):
        """PATCH com status válido deve ter sucesso."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.patch(
            f"/api/v1/weddings/{wedding.uuid}/",
            data={"status": "CANCELED"},
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELED"

    def test_update_wedding_invalid_status_returns_422(self, auth_client, user):
        """PATCH com status inválido deve retornar 422 (Schema validation error)."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.patch(
            f"/api/v1/weddings/{wedding.uuid}/",
            data={"status": "INVALID_STATUS"},
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_delete_wedding_success(self, auth_client, user):
        """DELETE deve remover um casamento."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.delete(f"/api/v1/weddings/{wedding.uuid}/")

        assert response.status_code == 204

    def test_list_weddings_by_month_success(self, auth_client, user):
        """GET /api/v1/weddings/by-month/?year=<future> retorna contagens."""
        FUTURE_YEAR = date.today().year + 1
        WeddingFactory(company=user.company, date=date(FUTURE_YEAR, 1, 15))
        WeddingFactory(company=user.company, date=date(FUTURE_YEAR, 1, 20))
        response = auth_client.get("/api/v1/weddings/by-month/", {"year": FUTURE_YEAR})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["month"] == 1
        assert data[0]["count"] == 2

    def test_list_weddings_by_month_multitenancy(self, auth_client, user):
        """Usuário só vê seus próprios casamentos."""
        FUTURE_YEAR = date.today().year + 1
        WeddingFactory(company=user.company, date=date(FUTURE_YEAR, 1, 15))
        response = auth_client.get("/api/v1/weddings/by-month/", {"year": FUTURE_YEAR})
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

    def test_list_weddings_lookup_success(self, auth_client, user):
        """GET /api/v1/weddings/lookup/ retorna lista simplificada
        ordenada por bride_name.
        """
        WeddingFactory(company=user.company, bride_name="Zélia", groom_name="Beto")
        WeddingFactory(company=user.company, bride_name="Beatriz", groom_name="Carlos")

        response = auth_client.get("/api/v1/weddings/lookup/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["bride_name"] == "Beatriz"
        assert data[0]["groom_name"] == "Carlos"
        assert "uuid" in data[0]
        assert "location" not in data[0]
        assert "date" not in data[0]
        assert data[1]["bride_name"] == "Zélia"

    def test_list_weddings_lookup_multitenancy(self, auth_client, user):
        """GET /api/v1/weddings/lookup/ respeita o isolamento multi-tenant."""
        from apps.users.tests.factories import UserFactory

        other_user = UserFactory()
        WeddingFactory(company=user.company, bride_name="Minha Noiva")
        WeddingFactory(company=other_user.company, bride_name="Noiva Alheia")

        response = auth_client.get("/api/v1/weddings/lookup/")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["bride_name"] == "Minha Noiva"

    def test_complete_wedding_api_success(self, auth_client, user):
        """POST /api/v1/weddings/{uuid}/complete/ conclui casamento válido."""
        today = timezone.now().date()
        wedding = WeddingFactory(company=user.company, date=today)

        response = auth_client.post(f"/api/v1/weddings/{wedding.uuid}/complete/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "COMPLETED"

    def test_complete_wedding_api_premature_returns_422(self, auth_client, user):
        """POST /api/v1/weddings/{uuid}/complete/ rejeita conclusão antes da data."""
        future_date = timezone.now().date() + timedelta(days=5)
        wedding = WeddingFactory(company=user.company, date=future_date)

        response = auth_client.post(f"/api/v1/weddings/{wedding.uuid}/complete/")

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "wedding_premature_completion"

    def test_complete_wedding_api_cross_tenant_returns_404(self, auth_client):
        """POST /api/v1/weddings/{uuid}/complete/ respeita isolamento de tenant."""
        other_wedding = WeddingFactory()

        response = auth_client.post(f"/api/v1/weddings/{other_wedding.uuid}/complete/")

        assert response.status_code == 404

    def test_cancel_wedding_api_success(self, auth_client, user):
        """POST /api/v1/weddings/{uuid}/cancel/ cancela casamento em andamento."""
        wedding = WeddingFactory(company=user.company)

        response = auth_client.post(f"/api/v1/weddings/{wedding.uuid}/cancel/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "CANCELED"

    def test_cancel_wedding_api_cross_tenant_returns_404(self, auth_client):
        """POST /api/v1/weddings/{uuid}/cancel/ respeita isolamento de tenant."""
        other_wedding = WeddingFactory()

        response = auth_client.post(f"/api/v1/weddings/{other_wedding.uuid}/cancel/")

        assert response.status_code == 404

    def test_reopen_wedding_api_success(self, auth_client: Any, user: Any) -> None:
        """POST /api/v1/weddings/{uuid}/reopen/ reabre casamento cancelado."""
        wedding = WeddingFactory(
            company=user.company, status=Wedding.StatusChoices.CANCELED
        )

        response = auth_client.post(f"/api/v1/weddings/{wedding.uuid}/reopen/")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "IN_PROGRESS"

    def test_reopen_wedding_api_invalid_transition_returns_422(
        self, auth_client: Any, user: Any
    ) -> None:
        """POST /api/v1/weddings/{uuid}/reopen/ rejeita reabrir casamento concluído."""
        wedding = WeddingFactory(
            company=user.company,
            date=timezone.now().date(),
            status=Wedding.StatusChoices.COMPLETED,
        )

        response = auth_client.post(f"/api/v1/weddings/{wedding.uuid}/reopen/")

        assert response.status_code == 422
        body = response.json()
        assert body["code"] == "wedding_invalid_status_transition"

    def test_reopen_wedding_api_cross_tenant_returns_404(
        self, auth_client: Any
    ) -> None:
        """POST /api/v1/weddings/{uuid}/reopen/ respeita isolamento de tenant."""
        other_wedding = WeddingFactory(status=Wedding.StatusChoices.CANCELED)

        response = auth_client.post(f"/api/v1/weddings/{other_wedding.uuid}/reopen/")

        assert response.status_code == 404

    def test_wedding_out_serialization_allowed_transitions_and_can_complete(
        self, auth_client: Any, user: Any
    ) -> None:
        """WeddingOut serializa allowed_transitions e can_complete corretamente."""
        today = timezone.now().date()
        future_date = today + timedelta(days=60)

        # 1. Casamento futuro em andamento
        future_wedding = WeddingFactory(company=user.company, date=future_date)
        res_future = auth_client.get(f"/api/v1/weddings/{future_wedding.uuid}/")
        assert res_future.status_code == 200
        data_future = res_future.json()
        assert data_future["status"] == "IN_PROGRESS"
        assert set(data_future["allowed_transitions"]) == {"COMPLETED", "CANCELED"}
        assert data_future["can_complete"] is False

        # 2. Casamento de hoje em andamento
        today_wedding = WeddingFactory(company=user.company, date=today)
        res_today = auth_client.get(f"/api/v1/weddings/{today_wedding.uuid}/")
        assert res_today.status_code == 200
        data_today = res_today.json()
        assert data_today["status"] == "IN_PROGRESS"
        assert data_today["can_complete"] is True

        # 3. Casamento cancelado
        canceled_wedding = WeddingFactory(
            company=user.company, status=Wedding.StatusChoices.CANCELED
        )
        res_canceled = auth_client.get(f"/api/v1/weddings/{canceled_wedding.uuid}/")
        assert res_canceled.status_code == 200
        data_canceled = res_canceled.json()
        assert data_canceled["allowed_transitions"] == ["IN_PROGRESS"]
        assert data_canceled["can_complete"] is False

        # 4. Casamento concluído
        completed_wedding = WeddingFactory(
            company=user.company, date=today, status=Wedding.StatusChoices.COMPLETED
        )
        res_completed = auth_client.get(f"/api/v1/weddings/{completed_wedding.uuid}/")
        assert res_completed.status_code == 200
        data_completed = res_completed.json()
        assert data_completed["allowed_transitions"] == []
        assert data_completed["can_complete"] is True
