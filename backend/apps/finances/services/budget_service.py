import logging
from typing import Any

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.finances.models import Budget


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
    def get(instance_or_uuid: Any, user: AuthContextUser | None = None) -> Budget:
        """
        Recupera um orçamento.
        Se receber UUID, exige user para garantir multitenancy.
        """
        if isinstance(instance_or_uuid, Budget):
            return instance_or_uuid

        try:
            qs = Budget.objects.all()
            if user:
                qs = Budget.objects.for_user(user)
            return qs.select_related("wedding").get(uuid=instance_or_uuid)
        except Budget.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Orçamento não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(data: dict[str, Any]) -> Budget:
        logger.info("Iniciando criação de Orçamento Mestre")

        wedding = data.pop("wedding")
        # Se for UUID e não tivermos o wedding resolvido, o service vai explodir.
        # Mas o Controller deve garantir que 'wedding' seja uma instância.

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
    def get_or_create_for_wedding(user: AuthContextUser, wedding_id: Any) -> Budget:
        from apps.core.dependencies import resolve_wedding_for_user
        from apps.finances.services.budget_category_service import (
            BudgetCategoryService,
        )

        wedding = resolve_wedding_for_user(user, wedding_id)

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
