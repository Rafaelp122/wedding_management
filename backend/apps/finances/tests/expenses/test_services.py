from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.finances.models import Expense
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import BudgetCategoryFactory, ExpenseFactory
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestExpenseService:
    """Testes de lógica de negócio para ExpenseService - Foco em Cobertura."""

    def test_list_expenses_with_filter(self, user):
        wedding = WeddingFactory(planner=user)
        cat = BudgetCategoryFactory(wedding=wedding)
        ExpenseFactory(wedding=wedding, category=cat)
        # Outro wedding do mesmo planner
        other_wedding = WeddingFactory(planner=user)
        ExpenseFactory(wedding=other_wedding)

        qs = ExpenseService.list(user, wedding_id=wedding.uuid)
        assert qs.count() == 1

    def test_create_expense_with_contract(self, user):
        wedding = WeddingFactory(planner=user)
        cat = BudgetCategoryFactory(wedding=wedding)
        contract = ContractFactory(wedding=wedding)

        data = {
            "category": cat.uuid,
            "contract": contract.uuid,
            "description": "Buffet",
            "estimated_amount": "5000.00",
        }
        expense = ExpenseService.create(user, data)
        assert expense.contract == contract

    def test_create_expense_validation_error(self, user):
        cat = BudgetCategoryFactory(wedding__planner=user)
        # 100.00 de valor real sem parcelas fere a Tolerância Zero (ADR-010)
        data = {
            "category": cat.uuid,
            "description": "A",
            "estimated_amount": 100,
            "actual_amount": 100,
        }
        with pytest.raises(BusinessRuleViolation):
            ExpenseService.create(user, data)

    def test_update_expense_contract(self, user):
        # actual_amount=0 é agora o default na factory
        expense = ExpenseFactory(wedding__planner=user, contract=None)
        new_contract = ContractFactory(wedding=expense.wedding)

        # 1. Vincular contrato
        updated = ExpenseService.update(user, expense, {"contract": new_contract.uuid})
        assert updated.contract == new_contract

        # 2. Desvincular contrato
        updated = ExpenseService.update(user, expense, {"contract": None})
        assert updated.contract is None

    def test_delete_expense_protected_error(self, user):
        expense = ExpenseFactory(wedding__planner=user)

        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar esta despesa"
        ):
            with patch.object(
                Expense, "delete", side_effect=ProtectedError("Erro", [])
            ):
                ExpenseService.delete(expense)
