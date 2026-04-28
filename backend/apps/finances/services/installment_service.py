import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.finances.models import Expense, Installment


logger = logging.getLogger(__name__)


class InstallmentService:
    """
    Camada de serviço para orquestração de Parcelas.
    Purificada: Recebe instâncias resolvidas.
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Installment]:
        return Installment.objects.for_user(user).select_related("expense", "wedding")

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Installment:
        logger.info("Iniciando criação de Parcela")

        # 1. Resolução Segura de Dependências
        expense_input = data.pop("expense")
        expense = Expense.objects.resolve(user, expense_input)

        # 2. Injeção de Contexto e Instanciação
        installment = Installment(wedding=expense.wedding, expense=expense, **data)

        # 3. Validação Estrita da Parcela
        installment.save()

        # 4. Checagem de Ricochete (Tolerância Zero)
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            raise BusinessRuleViolation(
                detail=(
                    "A criação desta parcela gera uma inconsistência matemática "
                    "na despesa total (ADR-010). O valor das parcelas deve bater "
                    "exatamente com o total."
                ),
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela criada com sucesso: uuid={installment.uuid}")
        return installment

    @staticmethod
    @transaction.atomic
    def update(instance: Installment, data: dict[str, Any]) -> Installment:
        logger.info(f"Atualizando Parcela uuid={instance.uuid}")

        # Proteção de campos estruturais
        data.pop("expense", None)
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        # Revalidação da Despesa Pai (Tolerância Zero)
        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            raise BusinessRuleViolation(
                detail="A atualização desta parcela viola as regras matemáticas da "
                "despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Installment) -> None:
        logger.info(f"Deletando Parcela uuid={instance.uuid}")
        expense = instance.expense

        try:
            instance.delete()
            expense.full_clean()

        except DjangoValidationError as e:
            # Rollback via @transaction.atomic
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta parcela isoladamente pois isso "
                    "quebra a soma exata da despesa (ADR-010). Ajuste as "
                    "outras parcelas ou a despesa simultaneamente."
                ),
                code="installment_deletion_math_error",
            ) from e

        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar esta parcela no momento.",
                code="installment_protected_error",
            ) from e
