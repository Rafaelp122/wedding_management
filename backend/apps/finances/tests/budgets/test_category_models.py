from decimal import Decimal

import pytest

from apps.finances.models.installment import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestBudgetCategoryTotalSpent:
    """Testes da computed property total_spent em BudgetCategory."""

    def test_total_spent_with_no_expenses(self, user):
        """Sem despesas, total_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        assert category.total_spent == Decimal("0.00")

    def test_total_spent_only_paid_installments(self, user):
        """total_spent soma apenas parcelas PAID, ignorando PENDING."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("6000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("3000.00")

    def test_total_spent_all_pending_returns_zero(self, user):
        """Todas as parcelas PENDING: total_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("4000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("4000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("0.00")

    def test_total_spent_multiple_expenses_mixed_status(self, user):
        """Soma PAID de múltiplas despesas, ignorando PENDING em todas."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)

        exp1 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("3000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=exp1,
            amount=Decimal("3000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-01-15",
        )

        exp2 = ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=Decimal("2000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=exp2,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PAID,
            paid_date="2026-02-15",
        )
        InstallmentFactory(
            expense=exp2,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert category.total_spent == Decimal("4000.00")
