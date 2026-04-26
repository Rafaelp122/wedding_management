from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.api
class TestWeddingNinjaAPI:
    """
    Testes de integração da API (Contrato e Segurança).
    """

    @pytest.mark.multitenancy
    def test_list_weddings_isolation(self, auth_client, user):
        """RF-SEC01: Planner só vê seus casamentos."""
        WeddingFactory(planner=user, bride_name="Noiva do User")
        WeddingFactory(bride_name="Noiva Alheia")

        response = auth_client.get("/api/v1/weddings/")

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["bride_name"] == "Noiva do User"

    def test_retrieve_wedding_success(self, auth_client, user):
        """Garante retorno 200 e payload tipado corretamente."""
        wedding = WeddingFactory(planner=user, bride_name="Maria")

        response = auth_client.get(f"/api/v1/weddings/{wedding.uuid}/")

        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == str(wedding.uuid)
        assert data["bride_name"] == "Maria"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_wedding_forbidden_for_other_planner(self, auth_client):
        """RF-SEC02: Acessar recurso alheio retorna 404."""
        other_wedding = WeddingFactory(bride_name="Noiva Secreta")

        response = auth_client.get(f"/api/v1/weddings/{other_wedding.uuid}/")

        assert response.status_code == 404

    def test_create_wedding_via_api_success(self, auth_client, user):
        """Garante fluxo de criação via API."""
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
        assert Wedding.objects.filter(planner=user).count() == 1

    @pytest.mark.security
    def test_update_attempt_to_change_planner_is_ignored(self, auth_client, user):
        """Segurança: Não é possível mudar o dono via PATCH."""
        from apps.users.tests.factories import UserFactory

        original_planner = user
        wedding = WeddingFactory(planner=original_planner)
        other_user = UserFactory()

        payload = {"planner_id": other_user.id}

        response = auth_client.patch(
            f"/api/v1/weddings/{wedding.uuid}/",
            data=payload,
            content_type="application/json",
        )

        assert response.status_code == 200
        wedding.refresh_from_db()
        assert wedding.planner == original_planner

    def test_delete_wedding_success(self, auth_client, user):
        """Garante remoção lógica/física e retorno 204."""
        wedding = WeddingFactory(planner=user)
        response = auth_client.delete(f"/api/v1/weddings/{wedding.uuid}/")
        assert response.status_code == 204
        assert Wedding.objects.count() == 0

    def test_create_wedding_with_past_date_returns_422(self, auth_client):
        """Validação: Payload inválido retorna 422."""
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

    def test_malformed_uuid_returns_422(self, auth_client):
        """Tipo de Dado: URL com formato inválido bloqueado pelo Ninja."""
        response = auth_client.get("/api/v1/weddings/not-a-uuid/")
        assert response.status_code == 422

    @pytest.mark.security
    def test_unauthenticated_access_denied(self, client):
        """Garante 401 para falta de token."""
        response = client.get("/api/v1/weddings/")
        assert response.status_code == 401


@pytest.mark.django_db
@pytest.mark.api
@pytest.mark.security
def test_get_wedding_dependency_logic(rf, user):
    """Testa diretamente a função auxiliar de autorização."""
    from apps.core.dependencies import get_wedding

    request = rf.get("/")
    request.user = user

    # 1. Caso 404 (Não existe)
    from apps.core.exceptions import ObjectNotFoundError

    with pytest.raises(ObjectNotFoundError):  # ObjectNotFoundError mapeia para 404
        get_wedding(request, uuid4())

    # 2. Caso Sucesso
    wedding = WeddingFactory(planner=user)
    result = get_wedding(request, wedding.uuid)
    assert result == wedding
