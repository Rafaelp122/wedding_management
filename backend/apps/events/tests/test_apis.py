from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.events.models import Event
from apps.events.tests.factories import EventFactory, WeddingFactory


@pytest.mark.django_db
@pytest.mark.api
class TestEventNinjaAPI:
    """
    Testes de integração da API (Contrato e Segurança).
    """

    @pytest.mark.multitenancy
    def test_list_events_isolation(self, auth_client, user):
        """RF-SEC01: Planner só vê seus eventos."""
        # Cria um evento vinculado ao user e outro alheio
        WeddingFactory(company=user.company, name="Meu Evento")
        WeddingFactory(name="Evento Alheio")

        # Endpoint genérico retorna apenas a base
        response = auth_client.get("/api/v1/events/")

        assert response.status_code == 200
        data = response.json()
        # O paginate do ninja retorna {"items": [], "count": X}
        items = data.get("items", data)
        assert len(items) == 1
        assert items[0]["name"] == "Meu Evento"

    def test_retrieve_event_success(self, auth_client, user):
        """Garante retorno 200 e payload polimórfico (com detalhes)."""
        event = WeddingFactory(company=user.company, bride_name="Maria")

        response = auth_client.get(f"/api/v1/events/{event.uuid}/")

        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == str(event.uuid)
        # No retorno polimórfico, o detalhe vem aninhado
        assert data["wedding_detail"]["bride_name"] == "Maria"

    def test_list_weddings_success(self, auth_client, user):
        """Garante listagem rica apenas de casamentos."""
        WeddingFactory(company=user.company, name="Casamento A")
        EventFactory(company=user.company, name="Outro Evento", event_type="OTHER")

        response = auth_client.get("/api/v1/events/weddings/")

        assert response.status_code == 200
        items = response.json().get("items", [])
        assert len(items) == 1
        assert items[0]["name"] == "Casamento A"
        assert "wedding_detail" in items[0]

    def test_update_wedding_details_success(self, auth_client, user):
        """Garante que é possível atualizar nomes dos noivos via WeddingController."""
        event = WeddingFactory(company=user.company, bride_name="Original")
        payload = {
            "name": "Novo Nome",
            "event_type": "WEDDING",
            "date": event.date.isoformat(),
            "location": event.location,
            "wedding_detail": {"groom_name": "Noivo", "bride_name": "Noiva Atualizada"},
        }

        response = auth_client.patch(
            f"/api/v1/events/weddings/{event.uuid}/",
            data=payload,
            content_type="application/json",
        )

        assert response.status_code == 200
        data = response.json()
        assert data["wedding_detail"]["bride_name"] == "Noiva Atualizada"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_event_forbidden_for_other_planner(self, auth_client):
        """RF-SEC02: Acessar recurso alheio retorna 404."""
        other_event = WeddingFactory(name="Evento Secreto")

        response = auth_client.get(f"/api/v1/events/{other_event.uuid}/")

        assert response.status_code == 404

    def test_create_wedding_via_api_success(self, auth_client, user):
        """Garante fluxo de criação de Casamento via API especializada."""
        payload = {
            "name": "Casamento do Ano",
            "event_type": "WEDDING",
            "date": (timezone.now().date() + timedelta(days=30)).isoformat(),
            "location": "Espaço Alvorada",
            "expected_guests": 150,
            "wedding_detail": {
                "groom_name": "Rafael Ninja",
                "bride_name": "Noiva de Teste",
            },
        }

        # Bate no WeddingController
        response = auth_client.post(
            "/api/v1/events/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 201
        assert Event.objects.filter(company=user.company).count() == 1

    @pytest.mark.security
    def test_update_attempt_to_change_company_is_ignored(self, auth_client, user):
        """Segurança: Não é possível mudar o dono via PATCH."""
        from apps.users.tests.factories import UserFactory

        original_company = user.company
        event = EventFactory(company=original_company)
        other_user = UserFactory()  # Cria outro user com sua própria company via signal

        payload = {"company_id": str(other_user.company_id)}

        response = auth_client.patch(
            f"/api/v1/events/{event.uuid}/",
            data=payload,
            content_type="application/json",
        )

        assert response.status_code == 200
        event.refresh_from_db()
        assert event.company == original_company

    def test_delete_event_success(self, auth_client, user):
        """Garante remoção e retorno 204."""
        event = EventFactory(company=user.company)
        response = auth_client.delete(f"/api/v1/events/{event.uuid}/")
        assert response.status_code == 204
        assert Event.objects.filter(uuid=event.uuid).count() == 0

    def test_create_wedding_with_past_date_returns_422(self, auth_client):
        """Validação: Payload inválido retorna 422."""
        payload = {
            "name": "Casamento Passado",
            "event_type": "WEDDING",
            "date": (timezone.now().date() - timedelta(days=1)).isoformat(),
            "location": "Salão Teste",
            "expected_guests": 100,
            "wedding_detail": {"groom_name": "Noivo", "bride_name": "Noiva"},
        }

        response = auth_client.post(
            "/api/v1/events/weddings/", data=payload, content_type="application/json"
        )

        assert response.status_code == 422

    def test_malformed_uuid_returns_422(self, auth_client):
        """Tipo de Dado: URL com formato inválido bloqueado pelo Ninja."""
        response = auth_client.get("/api/v1/events/not-a-uuid/")
        assert response.status_code == 422

    @pytest.mark.security
    def test_unauthenticated_access_denied(self, client):
        """Garante 401 para falta de token."""
        response = client.get("/api/v1/events/")
        assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.security
def test_get_event_dependency_logic(rf, user):
    """Testa diretamente a função auxiliar de autorização."""
    from apps.events.dependencies import get_event

    request = rf.get("/")
    request.user = user

    # 1. Caso 404 (Não existe)
    from apps.core.exceptions import ObjectNotFoundError

    with pytest.raises(ObjectNotFoundError):
        get_event(request, uuid4())

    # 2. Caso Sucesso
    event = EventFactory(company=user.company)
    result = get_event(request, event.uuid)
    assert result == event
