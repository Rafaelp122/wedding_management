import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.finances.models import BudgetCategory, Expense
from apps.logistics.models import Contract


logger = logging.getLogger(__name__)


class ExpenseService:
    """
    Camada de serviço para orquestração de Despesas.
    Garante que gastos reais respeitem o contexto do casamento, os contratos
    e assegura a rastreabilidade estrita da operação.
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Expense]:
        return Expense.objects.for_user(user).select_related(
            "category", "contract", "wedding"
        )

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Expense:
        from django.shortcuts import get_object_or_404

        return get_object_or_404(
            Expense.objects.for_user(user).select_related(
                "category", "contract", "wedding"
            ),
            uuid=uuid,
        )

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Expense:
        logger.info(f"Iniciando criação de Despesa para planner_id={user.id}")

        # 1. Resolução Segura de Categoria (Suporta Instância ou UUID)
        category_input = data.pop("category", None)

        if isinstance(category_input, BudgetCategory):
            category = category_input
        else:
            try:
                category = BudgetCategory.objects.for_user(user).get(
                    uuid=category_input
                )
            except BudgetCategory.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de categoria inválida/negada: {category_input}"
                )
                raise BusinessRuleViolation(
                    detail="Categoria não encontrada ou acesso negado.",
                    code="budget_category_not_found_or_denied",
                ) from e

        # 2. Resolução de Contrato (Opcional)
        contract = None
        contract_input = data.pop("contract", None)

        if contract_input:
            if isinstance(contract_input, Contract):
                contract = contract_input
            else:
                try:
                    contract = Contract.objects.for_user(user).get(uuid=contract_input)
                except Contract.DoesNotExist as e:
                    logger.warning(
                        f"Tentativa de uso de contrato inválido/negado: "
                        f"{contract_input}"
                    )
                    raise BusinessRuleViolation(
                        detail="Contrato não encontrado ou acesso negado.",
                        code="contract_not_found_or_denied",
                    ) from e

        # 3. Injeção de Contexto (ADR-009) e Instanciação
        expense = Expense(
            wedding=category.wedding,
            category=category,
            contract=contract,
            **data,
        )

        # 4. Validação Estrita no Model
        # WeddingOwnedMixin validará se a Categoria e o Contrato pertencem ao mesmo
        # Wedding.
        # Expense.clean() validará se o valor não entra em conflito com o
        # Contrato.
        expense.save()

        logger.info(f"Despesa criada com sucesso: uuid={expense.uuid}")
        return expense

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: Expense, data: dict[str, Any]
    ) -> Expense:
        logger.info(
            f"Atualizando Despesa uuid={instance.uuid} por planner_id={user.id}"
        )

        # Bloqueio de sequestro de contexto
        data.pop("planner", None)
        data.pop("wedding", None)
        data.pop("category", None)

        # Tratamento de troca ou desvinculação de contrato
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                if isinstance(contract_input, Contract):
                    instance.contract = contract_input
                else:
                    try:
                        instance.contract = Contract.objects.for_user(user).get(
                            uuid=contract_input
                        )
                    except Contract.DoesNotExist as e:
                        raise BusinessRuleViolation(
                            detail="Contrato inválido ou acesso negado.",
                            code="contract_not_found_or_denied",
                        ) from e
            else:
                instance.contract = None

        # Atualização dinâmica dos campos
        for field, value in data.items():
            setattr(instance, field, value)

        # Se o utilizador alterar o 'actual_amount' da despesa, e esta já tiver
        # parcelas (Installments) pagas, o full_clean() DEVE ser programado no Model
        # para explodir e bloquear a ação se violar a Tolerância Zero
        # (ADR-010).
        instance.save()

        logger.info(f"Despesa uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: Expense, data: dict[str, Any]
    ) -> Expense:
        return ExpenseService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: Expense) -> None:
        logger.info(
            f"Tentativa de deleção da Despesa uuid={instance.uuid} "
            f"por planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Despesa uuid={instance.uuid} DESTRUÍDA por planner_id={user.id}"
            )

        except ProtectedError as e:
            # Mesmo que penses que as parcelas têm CASCADE, a rede de segurança
            # é obrigatória. Amanhã alguém muda o Model para PROTECT e o teu código
            # rebenta.
            logger.error(
                f"Falha de integridade ao deletar Despesa uuid={instance.uuid}"
            )
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta despesa. Verifique se existem "
                    "registos financeiros ou pagamentos processados que "
                    "bloqueiem a exclusão."
                ),
                code="expense_protected_error",
            ) from e
