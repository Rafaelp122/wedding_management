from decimal import Decimal

import pytest

from apps.finances.managers import ExpenseQuerySet
from apps.finances.models import Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.weddings.tests.factories import WeddingFactory


def _setup_expense(user):
    wedding = WeddingFactory(user_context=user)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    expense = ExpenseFactory(
        wedding=wedding, category=category, actual_amount=Decimal("1500.00")
    )
    return wedding, expense


@pytest.mark.django_db
class TestExpenseQuerySet:
    def test_with_details_returns_expense_queryset(self, user):
        wedding, expense = _setup_expense(user)

        qs = Expense.objects.for_tenant(user.company).with_details()

        assert isinstance(qs, ExpenseQuerySet)
        assert qs.count() == 1

    def test_with_details_counts_mixed_installment_statuses(self, user):
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PAID,
        )
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.PENDING,
        )
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("500.00"),
            status=Installment.StatusChoices.OVERDUE,
        )

        result = Expense.objects.for_tenant(user.company).with_details().get(uuid=expense.uuid)

        assert result.installments_count == 3
        assert result.paid_installments_count == 1
        assert result.total_paid == Decimal("500.00")
        assert result.total_pending == Decimal("1000.00")

    def test_with_details_all_paid(self, user):
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PAID,
        )

        result = Expense.objects.for_tenant(user.company).with_details().get(uuid=expense.uuid)

        assert result.installments_count == 1
        assert result.paid_installments_count == 1
        assert result.total_paid == Decimal("1000.00")
        assert result.total_pending == Decimal("0.00")

    def test_with_details_all_pending(self, user):
        wedding, expense = _setup_expense(user)
        InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=Decimal("1000.00"),
            status=Installment.StatusChoices.PENDING,
        )

        result = Expense.objects.for_tenant(user.company).with_details().get(uuid=expense.uuid)

        assert result.total_paid == Decimal("0.00")
        assert result.total_pending == Decimal("1000.00")

    def test_with_details_no_installments(self, user):
        wedding, expense = _setup_expense(user)

        result = Expense.objects.for_tenant(user.company).with_details().get(uuid=expense.uuid)

        assert result.installments_count == 0
        assert result.paid_installments_count == 0
        assert result.total_paid == Decimal("0.00")
        assert result.total_pending == Decimal("0.00")
