from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.events.tests.factories import EventFactory
from apps.finances.models import Budget


@pytest.mark.django_db
@pytest.mark.unit
class TestBudgetModel:
    """Testes de integridade do modelo Budget."""

    def test_budget_str(self):
        # Usamos EventFactory.build pois só precisamos do nome para o __str__
        event = EventFactory.build(name="Casamento de Teste")
        budget = Budget(event=event, total_estimated=Decimal("50000.00"))
        # O modelo gera "Orçamento: Nome (Data) - R$ 50000.00"
        assert "Casamento de Teste" in str(budget)
        assert "50000.00" in str(budget)

    def test_total_estimated_cannot_be_negative(self, user):
        event = EventFactory(company=user.company)
        budget = Budget(event=event, total_estimated=Decimal("-1.00"))
        with pytest.raises(ValidationError):
            budget.full_clean()
