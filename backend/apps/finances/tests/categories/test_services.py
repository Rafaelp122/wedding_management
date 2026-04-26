import pytest

from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.finances.models import BudgetCategory
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestBudgetCategoryService:
    """Testes de lógica de negócio para BudgetCategoryService."""

    def test_get_category_logic(self, user):
        wedding = WeddingFactory(planner=user)
        BudgetService.get_or_create_for_wedding(user, wedding.uuid)
        cat = BudgetCategory.objects.filter(wedding=wedding).first()

        # Sucesso
        assert BudgetCategoryService.get(user, cat.uuid) == cat

        # 404
        from uuid import uuid4

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.get(user, uuid4())

    def test_create_category_with_foreign_wedding(self, user):
        other_wedding = WeddingFactory()  # Outro planner
        from apps.finances.services.budget_service import BudgetService

        other_budget = BudgetService.get_or_create_for_wedding(
            other_wedding.planner, other_wedding.uuid
        )

        with pytest.raises(ObjectNotFoundError):
            BudgetCategoryService.create(
                user, {"budget": other_budget.uuid, "name": "Hack"}
            )

    def test_update_category_protection(self, user):
        wedding = WeddingFactory(planner=user)
        BudgetService.get_or_create_for_wedding(user, wedding.uuid)
        cat = BudgetCategory.objects.filter(wedding=wedding).first()

        # O update deve ignorar tentativas de mudar casamento ou orçamento
        new_wedding = WeddingFactory(planner=user)
        updated = BudgetCategoryService.update(
            cat, {"wedding": new_wedding, "name": "Novo"}
        )
        assert updated.name == "Novo"
        assert updated.wedding == wedding  # Não mudou!

    def test_delete_category_protected_error(self, user):
        from unittest.mock import patch

        from django.db.models import ProtectedError

        wedding = WeddingFactory(planner=user)
        BudgetService.get_or_create_for_wedding(user, wedding.uuid)
        cat = BudgetCategory.objects.filter(wedding=wedding).first()

        msg = "existem contratos ou despesas"
        with pytest.raises(DomainIntegrityError, match=msg):
            with patch.object(
                BudgetCategory, "delete", side_effect=ProtectedError("Erro", [])
            ):
                BudgetCategoryService.delete(cat)
