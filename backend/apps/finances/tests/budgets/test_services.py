from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError
from apps.finances.models import Budget, BudgetCategory
from apps.finances.services.budget_service import BudgetService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestBudgetService:
    def test_get_or_create_for_wedding_lazy_loading(self, user):
        wedding = WeddingFactory(planner=user)
        assert Budget.objects.filter(wedding=wedding).count() == 0
        budget1 = BudgetService.get_or_create_for_wedding(user, wedding.uuid)
        assert Budget.objects.filter(wedding=wedding).count() == 1
        assert budget1.total_estimated == 0
        assert BudgetCategory.objects.filter(budget=budget1).count() > 0

    def test_get_budget_polymorphism(self, user):
        """Domínio: get() aceita UUID ou Instância."""
        wedding = WeddingFactory(planner=user)
        budget = BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        # Caso 1: Por instância (user é ignorado mas obrigatório por tipo)
        assert BudgetService.get(budget, user=user) == budget

        # Caso 2: Por UUID com user
        assert BudgetService.get(budget.uuid, user=user) == budget

    def test_create_budget_duplicate_error(self, user):
        """Domínio: Garante que não se cria dois budgets para o mesmo wedding."""
        wedding = WeddingFactory(planner=user)
        BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        msg = "já possui um orçamento definido"
        with pytest.raises(DomainIntegrityError, match=msg):
            BudgetService.create({"wedding": wedding, "total_estimated": 100})

    def test_delete_budget_protected_error(self, user):
        wedding = WeddingFactory(planner=user)
        budget = BudgetService.get_or_create_for_wedding(user, wedding.uuid)

        msg = "existem categorias e despesas vinculadas"
        with pytest.raises(DomainIntegrityError, match=msg):
            with patch.object(Budget, "delete", side_effect=ProtectedError("Erro", [])):
                BudgetService.delete(budget)
