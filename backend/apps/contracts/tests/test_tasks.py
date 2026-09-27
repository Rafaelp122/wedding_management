"""Testes das tarefas assíncronas do domínio de Contratos (apps.contracts)."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal
from typing import Any, cast
from unittest.mock import MagicMock

import pytest

from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.tasks import on_contract_addendum_signed_task
from apps.contracts.tests.factories import (
    ContractAddendumFactory as _ContractAddendumFactory,
)
from apps.contracts.tests.factories import (
    SupplierContractFactory as _SupplierContractFactory,
)
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def SupplierContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _SupplierContractFactory(*args, **kwargs))


def ContractAddendumFactory(*args: Any, **kwargs: Any) -> ContractAddendum:
    return cast(ContractAddendum, _ContractAddendumFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Any:
    return _WeddingFactory(*args, **kwargs)


@pytest.mark.django_db
class TestOnContractAddendumSignedTask:
    """Valida a reação pós-commit à assinatura de aditivos."""

    def test_notifies_tenant_users_on_signed_addendum(
        self, user: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Task válida resolve a cadeia e notifica usuários ativos."""
        wedding = cast(Wedding, WeddingFactory(company=user.company))
        contract = SupplierContractFactory(
            company=user.company,
            wedding=wedding,
            total_amount=Decimal("5000.00"),
        )
        addendum = ContractAddendumFactory(
            company=user.company,
            wedding=wedding,
            contract=contract,
            amount=Decimal("1500.00"),
            status=ContractAddendum.StatusChoices.SIGNED,
            signed_date=dt.date.today(),
        )
        mock_notify = MagicMock()
        monkeypatch.setattr(
            "apps.notifications.interfaces.notify_contract_addendum_signed",
            mock_notify,
        )

        on_contract_addendum_signed_task.func(
            user.company.id,
            str(contract.uuid),
            str(addendum.uuid),
            str(addendum.amount),
        )

        mock_notify.assert_called_once()
        _, kwargs = mock_notify.call_args
        assert kwargs["company"] == user.company
        assert kwargs["addendum_uuid"] == addendum.uuid
        assert kwargs["addendum_amount"] == Decimal("1500.00")
        assert user in kwargs["users"]

    def test_ignores_missing_contract(
        self, user: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Contrato inexistente não dispara notificação nem exceção."""
        mock_notify = MagicMock()
        monkeypatch.setattr(
            "apps.notifications.interfaces.notify_contract_addendum_signed",
            mock_notify,
        )

        on_contract_addendum_signed_task.func(
            user.company.id,
            "00000000-0000-0000-0000-000000000000",
            "00000000-0000-0000-0000-000000000000",
            "100.00",
        )

        mock_notify.assert_not_called()
