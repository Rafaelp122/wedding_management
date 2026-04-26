"""
Configuração Local de Testes: App Finances.
"""

import pytest
from pytest_factoryboy import register

from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.weddings.services import WeddingService

from .factories import (
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
def finance_seed(db, user, django_user_model):
    """
    Cenário completo de isolamento financeiro (Multitenancy).
    Cria dados para o usuário autenticado e para um usuário alheio.
    """
    # Planner alvo (Meu)
    my_wedding = WeddingService.create(
        user,
        {
            "bride_name": "Minha",
            "groom_name": "Noiva",
            "location": "A",
            "date": "2026-10-11",
        },
    )
    my_budget = BudgetService.get_or_create_for_wedding(user, my_wedding.uuid)
    my_category = my_budget.categories.first()
    my_expense = ExpenseService.create(
        user,
        {
            "category": my_category,
            "description": "Despesa A",
            "estimated_amount": "100.00",
            "actual_amount": "0.00",
        },
    )

    # Planner alheio (Outro)
    other_user = django_user_model.objects.create_user(
        email="other@test.com", password="123"
    )
    other_wedding = WeddingService.create(
        other_user,
        {
            "bride_name": "Outra",
            "groom_name": "Outro",
            "location": "B",
            "date": "2026-10-11",
        },
    )
    other_budget = BudgetService.get_or_create_for_wedding(
        other_user, other_wedding.uuid
    )
    other_category = other_budget.categories.first()
    other_expense = ExpenseService.create(
        other_user,
        {
            "category": other_category,
            "description": "Despesa B",
            "estimated_amount": "200.00",
            "actual_amount": "0.00",
        },
    )

    return {
        "my_budget": my_budget,
        "my_category": my_category,
        "my_expense": my_expense,
        "other_user": other_user,
        "other_budget": other_budget,
        "other_expense": other_expense,
    }
