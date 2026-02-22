import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import Expense, Installment


logger = logging.getLogger(__name__)


class InstallmentService:
    """
    Camada de serviço para orquestração de Parcelas.
    Garante o isolamento multitenant e a integridade da Tolerância Zero (ADR-010)
    nas despesas pai.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Installment:
        logger.info(f"Iniciando criação de Parcela para planner_id={user.id}")

        # 1. Resolução Segura de Dependências
        expense_input = data.pop("expense", None)
        if isinstance(expense_input, Expense):
            expense = expense_input
        else:
            try:
                expense = Expense.objects.all().for_user(user).get(uuid=expense_input)
            except Expense.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de despesa inválida/negada: {expense_input}"
                )
                raise BusinessRuleViolation(
                    detail="Despesa não encontrada ou acesso negado.",
                    code="expense_not_found_or_denied",
                ) from e

        # 2. Injeção de Contexto e Instanciação
        # NOTA: O cálculo de status (OVERDUE, PENDING, PAID) foi expulso do Service.
        # Ele DEVE estar no método clean() do Model Installment.
        installment = Installment(
            planner=user, wedding=expense.wedding, expense=expense, **data
        )

        # 3. Validação Estrita da Parcela
        installment.full_clean()
        installment.save()

        # 4. Checagem de Ricochete (Tolerância Zero)
        # O full_clean() da Despesa verifica se a matemática global foi quebrada.
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            logger.error(
                f"Criação de parcela violou Tolerância Zero da despesa "
                f"uuid={expense.uuid}"
            )
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
    def update(instance: Installment, user, data: dict) -> Installment:
        logger.info(
            f"Atualizando Parcela uuid={instance.uuid} por planner_id={user.id}"
        )

        # Proteção de campos estruturais
        data.pop("expense", None)
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Status auto-update deve ser garantido pelo Model (clean/save).

        instance.full_clean()
        instance.save()

        # Revalidação da Despesa Pai (Tolerância Zero)
        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            logger.error(
                f"Atualização de parcela quebrou Tolerância Zero na despesa "
                f"uuid={instance.expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail="A atualização desta parcela viola as regras matemáticas da "
                "despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Installment) -> None:
        logger.info(
            f"Tentativa de deleção da Parcela uuid={instance.uuid} "
            f"por planner_id={user.id}"
        )
        expense = instance.expense

        try:
            instance.delete()

            # Checagem de Ricochete após deleção
            expense.full_clean()

            logger.warning(
                f"Parcela uuid={instance.uuid} DESTRUÍDA por planner_id={user.id}"
            )

        except DjangoValidationError as e:
            logger.error(
                f"Deleção de parcela quebrou integridade matemática da despesa "
                f"uuid={expense.uuid}"
            )
            # Graças ao @transaction.atomic, se cair aqui, o delete da parcela é anulado
            # (rollback).
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta parcela isoladamente pois isso "
                    "quebra a soma exata da despesa (ADR-010). Ajuste as "
                    "outras parcelas ou a despesa simultaneamente."
                ),
                code="installment_deletion_math_error",
            ) from e

        except ProtectedError as e:
            logger.error(f"Falha estrutural ao deletar parcela uuid={instance.uuid}")
            raise DomainIntegrityError(
                detail="Não é possível apagar esta parcela no momento.",
                code="installment_protected_error",
            ) from e
