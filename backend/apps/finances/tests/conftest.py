"""
Configuração Local de Testes: App Finances.

Este ficheiro regista as factories financeiras. Como as finanças são o coração
do sistema, estas fixtures permitem validar cálculos de impostos, parcelamento
e fluxos de caixa.
"""

from decimal import Decimal

import pytest
from pytest_factoryboy import register

from .model_factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)


# Registo das factories financeiras
register(BudgetFactory)
register(BudgetCategoryFactory)
register(ExpenseFactory)
register(InstallmentFactory)


@pytest.fixture
def budget_setup(db, budget_factory, budget_category_factory):
    """
    Fixture que prepara um cenário financeiro básico:
    Um orçamento com uma categoria já alocada.
    """
    budget = budget_factory.create(total_budget=Decimal("30000.00"))
    category = budget_category_factory.create(
        wedding=budget.wedding, name="Decoração", allocated_budget=Decimal("5000.00")
    )
    return budget, category


@pytest.fixture
def simple_expense(db, expense_factory):
    """Fixture que devolve uma despesa de R$ 1000,00 pronta para ser parcelada."""
    return expense_factory.create(actual_amount=Decimal("1000.00"))
