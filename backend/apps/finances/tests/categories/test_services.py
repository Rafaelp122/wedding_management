import pytest

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.events.tests.factories import EventFactory
from apps.finances.models import BudgetCategory
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService


@pytest.mark.django_db
@pytest.mark.service
class TestBudgetCategoryService:
    """Testes de lógica de negócio para BudgetCategoryService."""

    def test_get_category_logic(self, user):
        event = EventFactory(company=user.company)
        BudgetService.get_or_create_for_event(user, event.uuid)
        cat = BudgetCategory.objects.filter(event=event).first()

        # Sucesso
        assert BudgetCategoryService.get(user, cat.uuid) == cat

        # 404
        from uuid import uuid4

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.get(user, uuid4())

    def test_create_category_with_foreign_event(self, user):
        other_event = EventFactory()  # Outra empresa
        from apps.finances.services.budget_service import BudgetService

        # Resolve o orçamento da outra empresa (simulando acesso indevido)
        other_budget = BudgetService.setup_initial_budget(other_event)

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.create(
                user, {"budget": other_budget.uuid, "name": "Hack"}
            )

    def test_update_category_protection(self, user):
        event = EventFactory(company=user.company)
        BudgetService.get_or_create_for_event(user, event.uuid)
        cat = BudgetCategory.objects.filter(event=event).first()

        # O update deve ignorar tentativas de mudar evento ou orçamento
        new_event = EventFactory(company=user.company)
        updated = BudgetCategoryService.update(
            cat, {"event": new_event, "name": "Novo"}
        )
        assert updated.name == "Novo"
        assert updated.event == event  # Não mudou!

    def test_delete_category_protected_error(self, user):
        from unittest.mock import patch

        from django.db.models import ProtectedError

        event = EventFactory(company=user.company)
        BudgetService.get_or_create_for_event(user, event.uuid)
        cat = BudgetCategory.objects.filter(event=event).first()

        msg = "existem contratos ou despesas"
        with pytest.raises(DomainIntegrityError, match=msg):
            with patch.object(
                BudgetCategory, "delete", side_effect=ProtectedError("Erro", [])
            ):
                BudgetCategoryService.delete(cat)
