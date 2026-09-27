"""
Testes unitários para os seletores de leitura do domínio de clientes.
"""

from typing import Any, cast
from uuid import uuid4

import pytest

from apps.clients.interfaces import get_client_for_tenant
from apps.clients.models import Client
from apps.clients.selectors import client_get_selector, client_list_selector
from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory


def ClientFactory(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestClientSelectors:
    """Testes dos seletores de consulta pura de clientes."""

    def test_client_list_selector_tenant_isolation(self) -> None:
        """Garante que a listagem traz apenas clientes do tenant solicitado."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()

        c1 = ClientFactory(company=company1, name="Bruno Silva")
        c2 = ClientFactory(company=company1, name="Carla Souza")
        ClientFactory(company=company2, name="Outro Cliente")

        result = list(client_list_selector(company=company1))
        assert len(result) == 2
        assert result[0] == c1
        assert result[1] == c2

    def test_client_list_selector_with_search_query(self) -> None:
        """Garante que a busca textual no seletor filtra corretamente."""
        company = CompanyFactory()
        c1 = ClientFactory(
            company=company, name="Fernanda Rocha", email="fernanda@exemplo.com"
        )
        ClientFactory(
            company=company, name="Rodrigo Alves", email="rodrigo@exemplo.com"
        )

        result = list(client_list_selector(company=company, q="Fernanda"))
        assert len(result) == 1
        assert result[0] == c1

    def test_client_get_selector_success(self) -> None:
        """Busca com sucesso um cliente por UUID."""
        company = CompanyFactory()
        client = ClientFactory(company=company)

        found = client_get_selector(company=company, uuid=client.uuid)
        assert found == client

    def test_client_get_selector_fails_cross_tenant(self) -> None:
        """Lança ObjectNotFoundError ao tentar acessar cliente de outro tenant."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()
        client = ClientFactory(company=company1)

        with pytest.raises(ObjectNotFoundError):
            client_get_selector(company=company2, uuid=client.uuid)

    def test_client_get_selector_not_found(self) -> None:
        """Lança ObjectNotFoundError para UUID inexistente."""
        company = CompanyFactory()
        with pytest.raises(ObjectNotFoundError):
            client_get_selector(company=company, uuid=uuid4())

    def test_get_client_for_tenant_interface(self) -> None:
        """Valida o funcionamento da fachada de interfaces públicas entre domínios."""
        company = CompanyFactory()
        client = ClientFactory(company=company)

        found = get_client_for_tenant(company=company, client_id=client.uuid)
        assert found == client
