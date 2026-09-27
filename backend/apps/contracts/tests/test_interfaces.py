from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, cast

import pytest

from apps.contracts.interfaces import (
    get_planner_contract_for_wedding,
    is_planner_contract_signed,
    save_planner_contract_for_wedding,
    sign_planner_contract_for_wedding,
)
from apps.contracts.models import Contract
from apps.contracts.tests.factories import (
    PlannerContractFactory as _PlannerContractFactory,
)
from apps.core.exceptions import BusinessRuleViolation
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


def PlannerContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _PlannerContractFactory(*args, **kwargs))


@pytest.mark.django_db
class TestContractInterfaces:
    """Testes unitários para as interfaces públicas de Contratos."""

    def test_get_planner_contract_for_wedding(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        assert (
            get_planner_contract_for_wedding(company=user.company, wedding=wedding)
            is None
        )

        contract = PlannerContractFactory(wedding=wedding, company=user.company)
        retrieved = get_planner_contract_for_wedding(
            company=user.company, wedding=wedding
        )
        assert retrieved is not None
        assert retrieved.uuid == contract.uuid

    def test_save_planner_contract_for_wedding_create_and_update(
        self, user: Any
    ) -> None:
        wedding = WeddingFactory(company=user.company)

        # 1. Criação
        contract, created = save_planner_contract_for_wedding(
            company=user.company,
            wedding=wedding,
            service_tier="COMPLETA",
            total_amount=Decimal("7500.00"),
            installments_count=3,
        )
        assert created is True
        assert contract.service_tier == "COMPLETA"
        assert contract.total_amount == Decimal("7500.00")
        assert contract.installments_count == 3
        assert contract.status == Contract.StatusChoices.DRAFT

        # 2. Atualização
        updated_contract, created = save_planner_contract_for_wedding(
            company=user.company,
            wedding=wedding,
            service_tier="PARCIAL",
            total_amount=Decimal("5000.00"),
        )
        assert created is False
        assert updated_contract.pk == contract.pk
        assert updated_contract.service_tier == "PARCIAL"
        assert updated_contract.total_amount == Decimal("5000.00")

    def test_is_and_sign_planner_contract_for_wedding(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        PlannerContractFactory(
            wedding=wedding,
            company=user.company,
            status=Contract.StatusChoices.DRAFT,
            signed_date=None,
        )

        assert (
            is_planner_contract_signed(company=user.company, wedding=wedding) is False
        )

        signed = sign_planner_contract_for_wedding(
            company=user.company,
            wedding=wedding,
            signed_date=date(2026, 10, 1),
        )
        assert signed.status == Contract.StatusChoices.SIGNED
        assert signed.signed_date == date(2026, 10, 1)
        assert is_planner_contract_signed(company=user.company, wedding=wedding) is True

    def test_sign_planner_contract_not_found_raises(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        with pytest.raises(BusinessRuleViolation, match="contrato de assessoria"):
            sign_planner_contract_for_wedding(company=user.company, wedding=wedding)
