"""Testes unitários para as interfaces públicas de Casamentos."""

import uuid
from typing import Any

import pytest

from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.interfaces import get_wedding_display_name
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestWeddingInterfaces:
    """Valida os contratos da fachada pública de casamentos."""

    def test_get_wedding_display_name_success(self, user: Any) -> None:
        """Garante que o nome formatado de exibição é retornado com sucesso."""
        wedding: Any = WeddingFactory(
            user_context=user,
            bride_name="Juliana",
            groom_name="Rodrigo",
        )

        display_name = get_wedding_display_name(
            company=user.company,
            wedding_uuid=wedding.uuid,
        )

        assert display_name == "Casamento de Juliana e Rodrigo"

    def test_get_wedding_display_name_isolated_per_tenant(self, user: Any) -> None:
        """Garante isolamento multitenant entre empresas distintas."""
        wedding: Any = WeddingFactory(
            user_context=user,
            bride_name="Juliana",
            groom_name="Rodrigo",
        )
        other_company: Any = CompanyFactory()

        display_name = get_wedding_display_name(
            company=other_company,
            wedding_uuid=wedding.uuid,
        )

        assert display_name is None

    def test_get_wedding_display_name_nonexistent_returns_none(self, user: Any) -> None:
        """Retorna None quando o UUID do casamento não existe."""
        display_name = get_wedding_display_name(
            company=user.company,
            wedding_uuid=uuid.uuid4(),
        )

        assert display_name is None
