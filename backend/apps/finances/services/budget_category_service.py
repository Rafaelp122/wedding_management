import builtins
import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.finances.models import Budget, BudgetCategory
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetCategoryService:
    """
    Camada de serviço para gestão de categorias de orçamento.
    Delega a validação matemática rigorosa de teto financeiro para o Model.
    """

    @staticmethod
    def list(
        user: AuthContextUser, wedding_id: UUID | None = None
    ) -> QuerySet[BudgetCategory]:
        """
        Lista categorias de orçamento de um planner,
        opcionalmente filtradas por casamento.
        A multitenancy é garantida pelo manager .for_user().
        """
        qs = BudgetCategory.objects.for_user(user).select_related("budget", "wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> BudgetCategory:
        """
        Recupera uma categoria específica validando a posse.
        """
        try:
            return (
                BudgetCategory.objects.for_user(user)
                .select_related("budget", "wedding")
                .get(uuid=uuid)
            )
        except BudgetCategory.DoesNotExist as e:
            raise ObjectNotFoundError(
                detail="Categoria de orçamento não encontrada.",
                code="budget_category_not_found",
            ) from e

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> BudgetCategory:
        from .budget_service import BudgetService

        logger.info("Criando categoria de orçamento")

        # O schema envia 'budget' (UUID), resolvemos a instância com segurança
        budget_input = data.pop("budget")
        budget = BudgetService.get(budget_input, user)
        wedding = budget.wedding

        category = BudgetCategory(wedding=wedding, budget=budget, **data)
        category.save()

        return category

    @staticmethod
    @transaction.atomic
    def update(instance: BudgetCategory, data: dict[str, Any]) -> BudgetCategory:
        logger.info(f"Atualizando categoria uuid={instance.uuid}")

        # Proteção: não se muda casamento ou orçamento de uma categoria
        data.pop("wedding", None)
        data.pop("budget", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: BudgetCategory) -> None:
        logger.info(f"Deletando categoria uuid={instance.uuid}")

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar esta categoria pois existem contratos "
                "ou despesas vinculadas a ela.",
                code="budget_category_protected",
            ) from e

    @staticmethod
    @transaction.atomic
    def setup_defaults(
        wedding: Wedding, budget: Budget
    ) -> builtins.list["BudgetCategory"]:
        from apps.core.constants import DEFAULT_BUDGET_CATEGORIES

        logger.info(f"Gerando categorias padrão para o casamento {wedding.uuid}")

        categories = []
        for name in DEFAULT_BUDGET_CATEGORIES:
            cat = BudgetCategory(
                wedding=wedding, budget=budget, name=name, allocated_budget=0
            )
            cat.save()
            categories.append(cat)

        return categories
