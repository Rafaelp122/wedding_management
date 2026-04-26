from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Expense
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestExpenseModel:
    """Testes de integridade física e regras de Tolerância Zero (ADR-010)."""

    def test_expense_str(self):
        expense = Expense(description="Buffet", estimated_amount=Decimal("5000.00"))
        assert str(expense) == "Buffet"

    def test_tolerancia_zero_math_integrity(self, user):
        """Regra Crítica: Soma das parcelas deve ser EXATA ao valor total."""
        wedding = WeddingFactory(planner=user)
        category = BudgetCategoryFactory(wedding=wedding)

        # 1. Cria despesa de 1000 usando a Factory (mais limpo e centralizado)
        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            description="Teste",
            actual_amount=Decimal("1000.00")
        )

        # 2. Cria parcela de 1000 (Soma bate)
        InstallmentFactory(
            expense=expense,
            amount=Decimal("1000.00"),
            installment_number=1
        )

        expense.full_clean() # Deve passar

        # 3. Altera o valor total da despesa para 1200 sem mexer na parcela
        expense.actual_amount = Decimal("1200.00")
        with pytest.raises(ValidationError, match="não bate com o valor total"):
            expense.full_clean()
