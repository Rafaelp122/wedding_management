from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Expense
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


def _setup_expense(user):
    """Helper: cria wedding + budget + category no contexto do user."""
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    return wedding, category


def _make_expense(user, category, **kwargs):
    """Helper: cria expense vinculado ao wedding da categoria."""
    return ExpenseFactory(
        wedding=category.wedding, category=category, contract=None, **kwargs
    )


@pytest.mark.django_db
class TestExpenseModelMetadata:
    """Testes de representação e metadados do modelo Expense."""

    def test_expense_ordering_by_created_at_descending(self, user):
        """Ordenação padrão deve ser por -created_at (mais recente primeiro)."""
        _, category = _setup_expense(user)
        e1 = _make_expense(user, category, description="Despesa Antiga")
        e2 = _make_expense(user, category, description="Despesa Nova")

        expenses = list(Expense.objects.all())
        assert expenses[0] == e2
        assert expenses[1] == e1


@pytest.mark.django_db
class TestExpenseToleranceZero:
    """Testes da regra de Tolerância Zero (ADR-010 / BR-F01)."""

    def test_expense_clean_passes_when_sum_matches(self, user):
        """Soma das parcelas == actual_amount deve passar na validação."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("333.33")
        )
        InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("333.33")
        )
        InstallmentFactory(
            expense=expense, installment_number=3, amount=Decimal("333.34")
        )

        expense.full_clean()

    def test_expense_clean_fails_when_sum_mismatch(self, user):
        """Soma das parcelas != actual_amount deve levantar ValidationError."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("1000.00"))

        InstallmentFactory(
            expense=expense, installment_number=1, amount=Decimal("400.00")
        )
        InstallmentFactory(
            expense=expense, installment_number=2, amount=Decimal("400.00")
        )

        with pytest.raises(ValidationError) as exc_info:
            expense.full_clean()

        assert "não bate" in str(exc_info.value).lower()

    def test_expense_clean_passes_with_zero_actual_amount(self, user):
        """Despesa com actual_amount = 0 deve passar (sem parcelas)."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("0.00"))
        expense.full_clean()

    def test_expense_clean_when_no_installments(self, user):
        """Sem parcelas criadas e actual_amount > 0: soma = 0, deve falhar."""
        _, category = _setup_expense(user)
        expense = _make_expense(user, category, actual_amount=Decimal("500.00"))

        with pytest.raises(ValidationError) as exc_info:
            expense.full_clean()

        assert "não bate" in str(exc_info.value).lower()
