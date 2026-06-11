from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Budget
from apps.finances.models.installment import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestBudgetModelMetadata:
    """Testes de representação e metadados do modelo Budget."""

    def test_budget_str_representation(self, user):
        """__str__ deve conter o nome do casamento e o total_estimated."""
        wedding = WeddingFactory(
            user_context=user, bride_name="Maria", groom_name="João"
        )
        budget = BudgetFactory(wedding=wedding, total_estimated=Decimal("50000.00"))

        result = str(budget)
        assert "Maria" in result
        assert "João" in result
        assert "50000.00" in result

    def test_budget_ordering_by_created_at_descending(self, user):
        """Ordenação padrão deve ser por -created_at."""
        w1 = WeddingFactory(user_context=user)
        w2 = WeddingFactory(user_context=user)
        b1 = BudgetFactory(wedding=w1)
        b2 = BudgetFactory(wedding=w2)

        budgets = list(Budget.objects.all())
        assert budgets[0] == b2
        assert budgets[1] == b1

    def test_budget_total_estimated_min_value(self, user):
        """total_estimated não pode ser negativo (MinValueValidator 0.00)."""
        wedding = WeddingFactory(user_context=user)
        budget = Budget(
            wedding=wedding, company=user.company, total_estimated=Decimal("-1.00")
        )

        with pytest.raises(ValidationError):
            budget.full_clean()

    def test_budget_total_estimated_zero_is_valid(self, user):
        """total_estimated = 0 é permitido."""
        wedding = WeddingFactory(user_context=user)
        budget = Budget(
            wedding=wedding, company=user.company, total_estimated=Decimal("0.00")
        )
        budget.full_clean()


@pytest.mark.django_db
class TestBudgetTotalOverallSpent:
    """Testes da computed property total_overall_spent."""

    def test_total_overall_spent_with_no_expenses(self, user):
        """Sem despesas, total_overall_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        assert budget.total_overall_spent == Decimal("0.00")

    def test_total_overall_spent_only_paid_installments(self, user):
        """total_overall_spent soma apenas parcelas PAID, ignorando PENDING."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        cat = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=cat,
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

        assert budget.total_overall_spent == Decimal("3000.00")

    def test_total_overall_spent_all_pending_returns_zero(self, user):
        """Todas as parcelas PENDING: total_overall_spent = 0."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        cat = BudgetCategoryFactory(budget=budget, wedding=wedding)

        expense = ExpenseFactory(
            wedding=wedding,
            category=cat,
            actual_amount=Decimal("4000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=expense,
            amount=Decimal("4000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert budget.total_overall_spent == Decimal("0.00")

    def test_total_overall_spent_multiple_categories_mixed_status(self, user):
        """Soma PAID de múltiplas categorias, ignorando PENDING de todas."""
        wedding = WeddingFactory(user_context=user)
        budget = BudgetFactory(wedding=wedding)
        cat1 = BudgetCategoryFactory(budget=budget, wedding=wedding)
        cat2 = BudgetCategoryFactory(budget=budget, wedding=wedding)

        exp1 = ExpenseFactory(
            wedding=wedding,
            category=cat1,
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
            category=cat2,
            actual_amount=Decimal("2000.00"),
            contract=None,
        )
        InstallmentFactory(
            expense=exp2,
            amount=Decimal("2000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        assert budget.total_overall_spent == Decimal("3000.00")
