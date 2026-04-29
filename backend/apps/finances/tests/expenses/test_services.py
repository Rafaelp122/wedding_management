from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.events.tests.factories import EventFactory
from apps.finances.models import Expense
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import BudgetCategoryFactory, ExpenseFactory
from apps.logistics.tests.factories import ContractFactory


@pytest.mark.django_db
@pytest.mark.service
class TestExpenseService:
    """Testes de lógica de negócio para ExpenseService - Foco em Cobertura."""

    def test_list_expenses_with_filter(self, user):
        event = EventFactory(company=user.company)
        cat = BudgetCategoryFactory(event=event)
        ExpenseFactory(event=event, category=cat)
        # Outro event do mesmo planner
        other_event = EventFactory(company=user.company)
        ExpenseFactory(event=other_event)

        qs = ExpenseService.list(user, event_id=event.uuid)
        assert qs.count() == 1

    def test_create_expense_with_contract(self, user):
        event = EventFactory(company=user.company)
        cat = BudgetCategoryFactory(event=event)
        contract = ContractFactory(event=event)

        data = {
            "category": cat.uuid,
            "contract": contract.uuid,
            "description": "Buffet",
            "estimated_amount": "5000.00",
        }
        expense = ExpenseService.create(user, data)
        assert expense.contract == contract

    def test_create_expense_validation_error(self, user):
        cat = BudgetCategoryFactory(event__company=user.company)
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
        expense = ExpenseFactory(event__company=user.company, contract=None)
        new_contract = ContractFactory(event=expense.event)

        # 1. Vincular contrato
        updated = ExpenseService.update(user, expense, {"contract": new_contract.uuid})
        assert updated.contract == new_contract

        # 2. Desvincular contrato
        updated = ExpenseService.update(user, expense, {"contract": None})
        assert updated.contract is None

    def test_delete_expense_protected_error(self, user):
        expense = ExpenseFactory(event__company=user.company)

        with pytest.raises(
            DomainIntegrityError, match="Não é possível apagar esta despesa"
        ):
            with patch.object(
                Expense, "delete", side_effect=ProtectedError("Erro", [])
            ):
                ExpenseService.delete(expense)
