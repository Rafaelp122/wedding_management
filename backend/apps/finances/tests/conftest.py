"""
Configuração Local de Testes: App Finances.

Fornece fixtures fábrica que eliminam o boilerplate de criação
da cadeia wedding → budget → category → expense → installment.
"""

from datetime import date, timedelta
from decimal import Decimal

import pytest
from pytest_factoryboy import register

from apps.finances.models import Installment
from apps.weddings.tests.factories import WeddingFactory

from .factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)


register(BudgetFactory)
register(BudgetCategoryFactory)
register(ExpenseFactory)
register(InstallmentFactory)


@pytest.fixture
def make_expense(user):
    """Factory fixture: cria wedding + budget + category + expense."""

    def _make(actual_amount=Decimal("5000.00"), **kwargs):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        return ExpenseFactory(
            wedding=wedding,
            category=category,
            actual_amount=actual_amount,
            **kwargs,
        )

    return _make


@pytest.fixture
def make_installment(user):
    """Factory fixture: cria toda a cadeia até uma parcela."""

    def _make(
        amount=Decimal("500.00"), status=Installment.StatusChoices.PENDING, **kwargs
    ):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget, wedding=wedding)
        expense = ExpenseFactory(
            wedding=wedding, category=category, actual_amount=amount
        )
        return InstallmentFactory(
            expense=expense,
            wedding=wedding,
            company=user.company,
            amount=amount,
            status=status,
            due_date=kwargs.pop("due_date", date.today() + timedelta(days=30)),
            **kwargs,
        )

    return _make
