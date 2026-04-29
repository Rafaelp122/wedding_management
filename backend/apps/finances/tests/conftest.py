"""
Configuração Local de Testes: App Finances.
"""

import pytest
from pytest_factoryboy import register

from apps.events.services.event_service import EventService
from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService

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
    # 1. Meu Tenant (Usuário autenticado)
    my_event = EventService.create(
        user,
        {
            "name": "Meu Casamento de Teste",
            "event_type": "WEDDING",
            "location": "Local A",
            "date": "2026-10-11",
            "wedding_detail": {
                "bride_name": "Minha",
                "groom_name": "Noiva",
            },
        },
    )
    # O Budget já é criado automaticamente pelo SIGNAL wedding_created
    my_budget = BudgetService.get_or_create_for_event(user, my_event.uuid)
    my_category = my_budget.categories.first()
    my_expense = ExpenseService.create(
        user,
        {
            "category": my_category.uuid,
            "description": "Despesa A",
            "estimated_amount": "100.00",
            "actual_amount": "0.00",
        },
    )

    # 2. Outro Tenant (Usuário alheio)
    other_user = django_user_model.objects.create_user(
        email="other_finance@test.com", password="123"
    )
    # O other_user ganha uma Company automaticamente via SIGNAL (create_user_company)

    other_event = EventService.create(
        other_user,
        {
            "name": "Evento Alheio",
            "event_type": "WEDDING",
            "location": "Local B",
            "date": "2026-10-11",
            "wedding_detail": {
                "bride_name": "Outra",
                "groom_name": "Outro",
            },
        },
    )
    other_budget = BudgetService.get_or_create_for_event(other_user, other_event.uuid)
    other_category = other_budget.categories.first()
    other_expense = ExpenseService.create(
        other_user,
        {
            "category": other_category.uuid,
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
