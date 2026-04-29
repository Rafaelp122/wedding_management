from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.events.tests.factories import EventFactory
from apps.finances.tests.factories import BudgetCategoryFactory, BudgetFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestBudgetCategoryModel:
    """Testes de integridade matemática e física da BudgetCategory (ADR-010)."""

    def test_category_sum_cannot_exceed_budget_total(self, user):
        """Regra Crítica ADR-010: Soma das categorias <= Teto do Orçamento."""
        event = EventFactory(company=user.company)
        # Teto de 1000.00
        budget = BudgetFactory(event=event, total_estimated=Decimal("1000.00"))

        # 1. Cria categoria que consome 60%
        BudgetCategoryFactory(
            event=event,
            budget=budget,
            name="Buffet",
            allocated_budget=Decimal("600.00"),
        )

        # 2. Tenta criar categoria que estoura o limite (mais 500 = 1100)
        invalid_cat = BudgetCategoryFactory.build(
            event=event,
            budget=budget,
            name="Foto",
            allocated_budget=Decimal("500.00"),
        )
        with pytest.raises(ValidationError, match="excede o teto do orçamento"):
            invalid_cat.clean()

    def test_category_update_validates_sum(self, user):
        """Garante que o update também valida o teto financeiro."""
        event = EventFactory(company=user.company)
        budget = BudgetFactory(event=event, total_estimated=Decimal("1000.00"))
        cat = BudgetCategoryFactory(
            event=event,
            budget=budget,
            name="Teste",
            allocated_budget=Decimal("100.00"),
        )

        cat.allocated_budget = Decimal("1100.00")
        with pytest.raises(ValidationError, match="excede o teto do orçamento"):
            cat.clean()
