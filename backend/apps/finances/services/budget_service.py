import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.finances.models import Budget
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """
    Camada de serviço para gestão do orçamento mestre.
    Garante que cada casamento tenha exatamente UM teto financeiro (OneToOne).
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Budget]:
        return Budget.objects.for_user(user).select_related("wedding")

    @staticmethod
    def get(instance_or_uuid: Budget | UUID | str, user: AuthContextUser) -> Budget:
        """
        Recupera um orçamento. Exige user para garantir multitenancy.
        """
        return Budget.objects.resolve(user, instance_or_uuid)

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Budget:
        logger.info("Iniciando criação de Orçamento Mestre")

        # Resolvemos o recurso pai (Wedding) vindo do JSON body
        wedding_id = data.pop("wedding")
        wedding = Wedding.objects.resolve(user, wedding_id)

        budget = Budget(wedding=wedding, **data)

        try:
            budget.save()
        except (IntegrityError, ValidationError) as e:
            if isinstance(e, ValidationError) and "wedding" not in e.message_dict:
                raise e

            raise DomainIntegrityError(
                detail="Este casamento já possui um orçamento definido.",
                code="budget_already_exists",
            ) from e

        return budget

    @staticmethod
    @transaction.atomic
    def update(instance: Budget, data: dict[str, Any]) -> Budget:
        logger.info(f"Atualizando Orçamento uuid={instance.uuid}")

        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Budget) -> None:
        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar este orçamento principal pois existem "
                "categorias e despesas vinculadas a ele.",
                code="budget_protected_error",
            ) from e

    @staticmethod
    @transaction.atomic
    def get_or_create_for_wedding(
        user: AuthContextUser, wedding_id: Wedding | UUID | str
    ) -> Budget:
        from apps.finances.services.budget_category_service import (
            BudgetCategoryService,
        )

        wedding = Wedding.objects.resolve(user, wedding_id)

        budget, created = Budget.objects.get_or_create(
            wedding=wedding,
            defaults={"total_estimated": 0},
        )

        if created:
            BudgetCategoryService.setup_defaults(
                wedding=wedding,
                budget=budget,
            )

        return budget
