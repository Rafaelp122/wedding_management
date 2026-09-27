from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock

import pytest

from apps.finances.interfaces import create_expense_from_planner_contract
from apps.finances.models import Budget
from apps.finances.tests.factories import BudgetCategoryFactory, BudgetFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestFinancesInterfaces:
    """Testes de integração das fachadas públicas (interfaces) de finanças."""

    def test_create_expense_from_planner_contract_freezes_baseline(
        self, user: Any
    ) -> None:
        """create_expense_from_planner_contract deve congelar o baseline_amount do orçamento."""
        wedding = WeddingFactory(user_context=user)
        contract = MagicMock()
        contract.total_amount = Decimal("8000.00")
        contract.service_tier = "COMPLETA"
        contract.installments_count = 2
        contract.signed_date = None
        contract.uuid = None
        contract.get_service_tier_display.return_value = "Assessoria Completa"

        expense = create_expense_from_planner_contract(
            company=user.company,
            wedding=wedding,
            planner_contract=contract,
        )

        budget = Budget.objects.get(company=user.company, wedding=wedding)
        assert budget.baseline_amount == Decimal("8000.00")
        assert budget.total_estimated == Decimal("8000.00")
        assert expense.actual_amount == Decimal("8000.00")

    def test_create_expense_from_planner_contract_with_existing_category_freezes_baseline(
        self, user: Any
    ) -> None:
        """Quando category_id é fornecido, o orçamento vinculado à categoria também é congelado."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(
            wedding=wedding,
            total_estimated=Decimal("15000.00"),
            baseline_amount=None,
        )
        category = BudgetCategoryFactory(
            budget=budget,
            wedding=wedding,
            allocated_budget=Decimal("5000.00"),
        )

        contract = MagicMock()
        contract.total_amount = Decimal("5000.00")
        contract.service_tier = "PARCIAL"
        contract.installments_count = 1
        contract.signed_date = None
        contract.uuid = None
        contract.get_service_tier_display.return_value = "Assessoria Parcial"

        create_expense_from_planner_contract(
            company=user.company,
            wedding=wedding,
            planner_contract=contract,
            category_id=category.uuid,
        )

        budget.refresh_from_db()
        assert budget.baseline_amount == Decimal("15000.00")
