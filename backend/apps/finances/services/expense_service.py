import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.types import AuthContextUser
from apps.finances.models import Expense


logger = logging.getLogger(__name__)


class ExpenseService:
    """
    Camada de serviço para orquestração de Despesas.
    Purificada: Recebe instâncias resolvidas.
    """

    @staticmethod
    def list(
        user: AuthContextUser, wedding_id: UUID | str | None = None
    ) -> QuerySet[Expense]:
        qs = Expense.objects.for_user(user).select_related(
            "category", "contract", "wedding"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Expense:
        """
        Cria uma despesa.
        Resolve dependências internas (Category/Contract) usando o user.
        """
        from apps.core.dependencies import (
            resolve_budget_category_for_user,
            resolve_contract_for_user,
        )

        logger.info("Iniciando criação de Despesa")

        # 1. Resolução Segura de Categoria
        category_input = data.pop("category")
        category = resolve_budget_category_for_user(user, category_input)

        # 2. Resolução de Contrato (Opcional)
        contract = None
        contract_input = data.pop("contract", None)
        if contract_input:
            contract = resolve_contract_for_user(user, contract_input)

        # 3. Injeção de Contexto e Instanciação
        expense = Expense(
            wedding=category.wedding,
            category=category,
            contract=contract,
            **data,
        )

        # 4. Validação e Persistência
        try:
            expense.save()
            # Força a checagem de Tolerância Zero (ADR-010) agora que possui PK
            expense.full_clean()
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="expense_validation_error",
            ) from e

        logger.info(f"Despesa criada com sucesso: uuid={expense.uuid}")
        return expense

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: Expense, data: dict[str, Any]
    ) -> Expense:
        from apps.core.dependencies import resolve_contract_for_user

        logger.info(f"Atualizando Despesa uuid={instance.uuid}")

        # Bloqueio de sequestro de contexto
        data.pop("planner", None)
        data.pop("wedding", None)
        data.pop("category", None)

        # Tratamento de troca ou desvinculação de contrato
        if "contract" in data:
            contract_input = data.pop("contract")
            instance.contract = (
                resolve_contract_for_user(user, contract_input)
                if contract_input
                else None
            )

        # Atualização dinâmica dos campos
        for field, value in data.items():
            setattr(instance, field, value)

        try:
            instance.save()
        except DjangoValidationError as e:
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="expense_validation_error",
            ) from e

        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Expense) -> None:
        logger.info(f"Deletando Despesa uuid={instance.uuid}")

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta despesa. Verifique se existem "
                    "registos financeiros ou pagamentos processados que "
                    "bloqueiem a exclusão."
                ),
                code="expense_protected_error",
            ) from e
