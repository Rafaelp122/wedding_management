"""
Testes unitários para a camada de serviços do domínio de clientes.
"""

from typing import Any, cast

import pytest

from apps.clients.models import Client
from apps.clients.schemas import ClientIn, ClientPatchIn
from apps.clients.services import ClientService
from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.core.exceptions import (
    BusinessRuleViolation,
    ObjectNotFoundError,
)
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory


def ClientFactory(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestClientService:
    """Testes dos casos de uso e mutações de ClientService."""

    def test_create_client_successfully(self) -> None:
        """Cria um cliente através do serviço com dados válidos."""
        company = CompanyFactory()
        payload = ClientIn(
            name="Juliana Ramos",
            cpf="12345678901",
            email="juliana@exemplo.com",
            phone="11999991111",
            notes="Cliente VIP",
        )

        client = ClientService.create(company=company, payload=payload)

        assert client.pk is not None
        assert client.name == "Juliana Ramos"
        assert client.email == "juliana@exemplo.com"
        assert client.company == company

    def test_create_client_fails_with_invalid_data(self) -> None:
        """Lança BusinessRuleViolation quando os dados violam o clean() do modelo."""
        company = CompanyFactory()
        payload = ClientIn.model_construct(
            name="",
            cpf="12345678901234567",
            email="invalido",
            phone="",
            notes="",
        )

        with pytest.raises(BusinessRuleViolation):
            ClientService.create(company=company, payload=payload)

    def test_update_client_successfully(self) -> None:
        """Atualiza parcialmente um cliente existente."""
        company = CompanyFactory()
        client = ClientFactory(
            company=company, name="Nome Antigo", email="antigo@exemplo.com"
        )

        payload = ClientPatchIn(name="Nome Atualizado", email="novo@exemplo.com")
        updated = ClientService.update(
            company=company, instance=client, payload=payload
        )

        assert updated.name == "Nome Atualizado"
        assert updated.email == "novo@exemplo.com"

    def test_update_client_denies_cross_tenant_access(self) -> None:
        """Lança ObjectNotFoundError ao tentar atualizar cliente de outro tenant."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()
        client = ClientFactory(company=company1)

        payload = ClientPatchIn(name="Hacker")
        with pytest.raises(ObjectNotFoundError):
            ClientService.update(company=company2, instance=client, payload=payload)

    def test_delete_client_successfully(self) -> None:
        """Exclui com sucesso um cliente sem vínculos impeditivos."""
        company = CompanyFactory()
        client = ClientFactory(company=company)

        ClientService.delete(company=company, instance=client)

        assert not Client.objects.filter(pk=client.pk).exists()

    @pytest.mark.skip(reason="Obsolete due to Phase 2 refactoring")
    @pytest.mark.skip(reason="Obsolete due to Phase 4 refactoring")
    def test_delete_client_protected_by_wedding_participant(self) -> None:
        pass

    def test_delete_client_denies_cross_tenant_access(self) -> None:
        """Lança ObjectNotFoundError ao excluir cliente de outro tenant."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()
        client = ClientFactory(company=company1)

        with pytest.raises(ObjectNotFoundError):
            ClientService.delete(company=company2, instance=client)
