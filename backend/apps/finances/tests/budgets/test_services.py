from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError
from apps.events.tests.factories import EventFactory
from apps.finances.models import Budget, BudgetCategory
from apps.finances.services.budget_service import BudgetService


@pytest.mark.django_db
@pytest.mark.service
class TestBudgetService:
    def test_get_or_create_for_event_lazy_loading(self, user):
        event = EventFactory(company=user.company)
        assert Budget.objects.filter(event=event).count() == 0
        budget1 = BudgetService.get_or_create_for_event(user, event.uuid)
        assert Budget.objects.filter(event=event).count() == 1
        assert budget1.total_estimated == 0
        assert BudgetCategory.objects.filter(budget=budget1).count() > 0

    def test_get_budget_polymorphism(self, user):
        """Domínio: get() aceita UUID ou Instância."""
        event = EventFactory(company=user.company)
        budget = BudgetService.get_or_create_for_event(user, event.uuid)

        # Caso 1: Por instância (user é ignorado mas obrigatório por tipo)
        assert BudgetService.get(budget, user=user) == budget

        # Caso 2: Por UUID com user
        assert BudgetService.get(budget.uuid, user=user) == budget

    def test_create_budget_duplicate_error(self, user):
        """Domínio: Garante que não se cria dois budgets para o mesmo event."""
        event = EventFactory(company=user.company)
        BudgetService.get_or_create_for_event(user, event.uuid)

        msg = "já possui um orçamento definido"
        with pytest.raises(DomainIntegrityError, match=msg):
            BudgetService.create(user, {"event": event, "total_estimated": 100})

    def test_delete_budget_protected_error(self, user):
        event = EventFactory(company=user.company)
        budget = BudgetService.get_or_create_for_event(user, event.uuid)

        msg = "existem categorias e despesas vinculadas"
        with pytest.raises(DomainIntegrityError, match=msg):
            with patch.object(Budget, "delete", side_effect=ProtectedError("Erro", [])):
                BudgetService.delete(budget)
