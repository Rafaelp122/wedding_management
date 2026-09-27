from __future__ import annotations

from typing import Any, cast

import pytest

from apps.clients.interfaces import (
    get_client_for_tenant,
    get_or_create_client_for_proposal,
)
from apps.clients.models import Client
from apps.clients.tests.factories import ClientFactory as _ClientFactory
from apps.core.exceptions import ObjectNotFoundError
from apps.users.tests.factories import UserFactory


def ClientFactory(*args: Any, **kwargs: Any) -> Client:
    return cast(Client, _ClientFactory(*args, **kwargs))


@pytest.mark.django_db
class TestClientInterfaces:
    """Testes unitários para as interfaces públicas de Clients."""

    def test_get_client_for_tenant_success(self, user: Any) -> None:
        client = ClientFactory(company=user.company)
        retrieved = get_client_for_tenant(company=user.company, client_id=client.uuid)
        assert retrieved.pk == client.pk

    def test_get_client_for_tenant_cross_tenant_raises_404(self, user: Any) -> None:
        other_user = UserFactory()
        other_client = ClientFactory(company=other_user.company)
        with pytest.raises(ObjectNotFoundError):
            get_client_for_tenant(company=user.company, client_id=other_client.uuid)

    def test_get_or_create_client_for_proposal_creates_new(self, user: Any) -> None:
        client = get_or_create_client_for_proposal(
            company=user.company,
            name="Mariana Santos",
            cpf="123.456.789-00",
            email="mariana@example.com",
            phone="11988887777",
        )
        assert client.pk is not None
        assert client.company == user.company
        assert client.name == "Mariana Santos"
        assert client.cpf == "123.456.789-00"
        assert client.email == "mariana@example.com"
        assert client.phone == "11988887777"

    def test_get_or_create_client_for_proposal_matches_existing_cpf(
        self, user: Any
    ) -> None:
        existing = ClientFactory(
            company=user.company,
            name="Mariana Original",
            cpf="123.456.789-00",
            email="",
            phone="",
        )

        client = get_or_create_client_for_proposal(
            company=user.company,
            name="Mariana Modificada",
            cpf="123.456.789-00",
            email="mariana.nova@example.com",
            phone="11999990000",
        )
        assert client.pk == existing.pk
        client.refresh_from_db()
        assert client.email == "mariana.nova@example.com"
        assert client.phone == "11999990000"
