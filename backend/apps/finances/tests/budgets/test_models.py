from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.finances.models import Budget
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestBudgetModel:
    """Testes de integridade do modelo Budget."""

    def test_budget_str(self):
        wedding = WeddingFactory.build(bride_name="Ana", groom_name="Beto")
        budget = Budget(wedding=wedding, total_estimated=Decimal("50000.00"))
        # O modelo gera "Orçamento: Beto & Ana..."
        assert "Beto & Ana" in str(budget)
        assert "50000.00" in str(budget)

    def test_total_estimated_cannot_be_negative(self, user):
        wedding = WeddingFactory(planner=user)
        budget = Budget(wedding=wedding, total_estimated=Decimal("-1.00"))
        with pytest.raises(ValidationError):
            budget.full_clean()
