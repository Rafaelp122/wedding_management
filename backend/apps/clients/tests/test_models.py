"""
Testes unitários para o modelo Client do domínio de clientes.
"""

from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError

from apps.clients.models import Client
from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.weddings.models import Wedding, WeddingClient
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def ClientFactory(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory(*args, **kwargs))


def _client_build(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory.build(*args, **kwargs))


ClientFactory.build = _client_build  # type: ignore[attr-defined]


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestClientModel:
    """Testes de integridade, sanitização e domínio do modelo Client."""

    def test_create_client_successfully(self) -> None:
        """Cria um cliente válido e valida os campos persistidos."""
        company = CompanyFactory()
        client = ClientFactory(
            company=company,
            name="  Maria da Silva  ",
            email="  MARIA@EXAMPLE.COM  ",
            phone="  (11) 99999-0000  ",
            cpf="  123.456.789-00 ",
        )

        assert client.pk is not None
        assert client.name == "Maria da Silva"
        assert client.email == "maria@example.com"
        assert client.phone == "(11) 99999-0000"
        assert client.cpf == "123.456.789-00"
        assert client.company == company

    def test_clean_fails_when_name_is_empty(self) -> None:
        """Valida que o clean() rejeita cliente com nome em branco."""
        company = CompanyFactory()
        client = _client_build(company=company, name="   ")

        with pytest.raises(ValidationError) as exc:
            client.full_clean()

        assert "name" in exc.value.message_dict

    def test_clean_fails_when_cpf_too_long(self) -> None:
        """Valida que o clean() rejeita CPF com mais de 14 caracteres."""
        company = CompanyFactory()
        client = _client_build(company=company, cpf="123456789012345")

        with pytest.raises(ValidationError) as exc:
            client.full_clean()

        assert "cpf" in exc.value.message_dict

    def test_str_representation(self) -> None:
        """Valida a representação textual do cliente com e sem CPF."""
        company = CompanyFactory()
        client_with_cpf = ClientFactory(
            company=company, name="João Silva", cpf="12345678900"
        )
        assert str(client_with_cpf) == "João Silva (12345678900)"

        client_without_cpf = ClientFactory(company=company, name="Ana Costa", cpf="")
        assert str(client_without_cpf) == "Ana Costa"

    def test_update_contact_info(self) -> None:
        """Valida o método de domínio de atualização cadastral."""
        company = CompanyFactory()
        client = ClientFactory(company=company, name="Carlos Souza")

        client.update_contact_info(
            name="Carlos Eduardo Souza",
            email="carlos@email.com",
            phone="11988887777",
            notes="Novo telefone",
        )
        client.save()

        client.refresh_from_db()
        assert client.name == "Carlos Eduardo Souza"
        assert client.email == "carlos@email.com"
        assert client.phone == "11988887777"
        assert client.notes == "Novo telefone"

    def test_manager_for_tenant_isolation(self) -> None:
        """Garante que for_tenant filtra estritamente pela empresa."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()

        c1 = ClientFactory(company=company1, name="Cliente C1")
        ClientFactory(company=company2, name="Cliente C2")

        from apps.clients.models import Client

        qs1 = Client.objects.for_tenant(company1)
        assert qs1.count() == 1
        assert qs1.first() == c1

    def test_manager_search(self) -> None:
        """Garante que a busca textual localiza por nome, e-mail, cpf ou telefone."""
        company = CompanyFactory()
        c1 = ClientFactory(
            company=company, name="Mariana Lima", email="mariana@test.com"
        )
        c2 = ClientFactory(company=company, name="Pedro Santos", phone="11911112222")
        c3 = ClientFactory(company=company, name="Lucas Oliveira", cpf="98765432100")

        from apps.clients.models import Client

        qs = Client.objects.for_tenant(company)
        assert qs.search("Mariana").first() == c1
        assert qs.search("11112222").first() == c2
        assert qs.search("98765432100").first() == c3


@pytest.mark.django_db
class TestWeddingClientModel:
    """Testes de integridade do vínculo WeddingClient."""

    @pytest.mark.skip(reason="Obsolete due to Phase 4 refactoring")
    def test_create_wedding_participant(self) -> None:
        pass

    @pytest.mark.skip(reason="Obsolete due to Phase 4 refactoring")
    def test_clean_fails_if_client_belongs_to_other_tenant(self) -> None:
        """Garante blindagem vertical contra cliente de outro tenant."""
        company1 = CompanyFactory()
        company2 = CompanyFactory()

        wedding = WeddingFactory(company=company1)
        client_other_company = ClientFactory(company=company2)

        participant = WeddingClient(
            company=company1,
            wedding=wedding,
            client=client_other_company,
            role=WeddingClient.RoleChoices.GROOM,
        )

        with pytest.raises(ValidationError) as exc:
            participant.full_clean()

        assert "client" in exc.value.message_dict

    @pytest.mark.skip(reason="Obsolete due to Phase 2 refactoring")
    @pytest.mark.skip(reason="Obsolete due to Phase 4 refactoring")
    def test_unique_together_wedding_client_role(self) -> None:
        pass
