"""
Testes de integração para os endpoints da API Ninja de clientes.
"""

from typing import Any, cast

import pytest

from apps.clients.models import Client
from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.users.models import User
from apps.weddings.models import Wedding, WeddingClient
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ClientFactory(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestClientNinjaAPI:
    """Testes dos endpoints REST de clientes (/api/v1/clients/)."""

    def test_list_clients_isolation(self, auth_client: Any, user: User) -> None:
        """Garante que a listagem de clientes respeita o isolamento de tenant."""
        c1 = ClientFactory(company=user.company, name="Cliente Meu")
        ClientFactory(name="Cliente Outro")

        response = auth_client.get("/api/v1/clients/")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["uuid"] == str(c1.uuid)
        assert data["items"][0]["name"] == "Cliente Meu"

    def test_list_clients_with_search_filter(
        self, auth_client: Any, user: User
    ) -> None:
        """Filtra clientes pelo parâmetro de query 'q'."""
        ClientFactory(company=user.company, name="Aline Silva", email="aline@email.com")
        ClientFactory(
            company=user.company, name="Bruno Castro", email="bruno@email.com"
        )

        response = auth_client.get("/api/v1/clients/?q=Aline")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["name"] == "Aline Silva"

    def test_create_client_success(self, auth_client: Any, user: User) -> None:
        """Cria cliente via POST /api/v1/clients/."""
        payload = {
            "name": "Camila Vasconcelos",
            "cpf": "12345678901",
            "email": "camila@teste.com",
            "phone": "11987654321",
            "notes": "Cliente indicada",
        }

        response = auth_client.post(
            "/api/v1/clients/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Camila Vasconcelos"
        assert data["email"] == "camila@teste.com"
        assert data["cpf"] == "12345678901"

    def test_create_client_validation_error(self, auth_client: Any, user: User) -> None:
        """Retorna 400 ou 422 em payload com dados inválidos."""
        payload = {
            "name": "",
        }

        response = auth_client.post(
            "/api/v1/clients/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code in (400, 422)

    def test_retrieve_client_success(self, auth_client: Any, user: User) -> None:
        """Recupera detalhes de cliente do próprio tenant."""
        client = ClientFactory(company=user.company, name="Daniel Souza")

        response = auth_client.get(f"/api/v1/clients/{client.uuid}/")
        assert response.status_code == 200
        data = response.json()
        assert data["uuid"] == str(client.uuid)
        assert data["name"] == "Daniel Souza"

    def test_retrieve_client_other_tenant_returns_404(
        self, auth_client: Any, user: User
    ) -> None:
        """Garante que cliente de outro tenant retorna 404 (sem leak de existência)."""
        other_client = ClientFactory()

        response = auth_client.get(f"/api/v1/clients/{other_client.uuid}/")
        assert response.status_code == 404

    def test_update_client_success(self, auth_client: Any, user: User) -> None:
        """Atualiza parcialmente um cliente via PATCH."""
        client = ClientFactory(company=user.company, name="Eduardo Antigo")

        payload = {"name": "Eduardo Novo", "notes": "Atualizado via API"}
        response = auth_client.patch(
            f"/api/v1/clients/{client.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Eduardo Novo"
        assert data["notes"] == "Atualizado via API"

    def test_update_client_other_tenant_returns_404(
        self, auth_client: Any, user: User
    ) -> None:
        """Rejeita atualização de cliente de outro tenant com 404."""
        other_client = ClientFactory(name="Intocável")

        response = auth_client.patch(
            f"/api/v1/clients/{other_client.uuid}/",
            data={"name": "Tentativa"},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_delete_client_success(self, auth_client: Any, user: User) -> None:
        """Exclui cliente sem vínculos com sucesso (204)."""
        client = ClientFactory(company=user.company)

        response = auth_client.delete(f"/api/v1/clients/{client.uuid}/")
        assert response.status_code == 204

        from apps.clients.models import Client

        assert not Client.objects.filter(pk=client.pk).exists()

    def test_delete_client_protected_returns_error(
        self, auth_client: Any, user: User
    ) -> None:
        """Tentativa de excluir cliente vinculado retorna 409 DomainIntegrityError."""

        client = ClientFactory(company=user.company)
        wedding = WeddingFactory(company=user.company)
        WeddingClient.objects.create(
            company=user.company,
            wedding=wedding,
            client=client,
            role=WeddingClient.RoleChoices.BRIDE,
        )

        response = auth_client.delete(f"/api/v1/clients/{client.uuid}/")
        assert response.status_code == 409
        assert response.json()["code"] == "client_protected_error"
