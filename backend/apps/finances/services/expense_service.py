import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import BudgetCategory, Expense
from apps.logistics.models import Contract
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class ExpenseService:
    """
    Camada de serviço para orquestração de Despesas.
    Garante que gastos reais respeitem o contexto do casamento, os contratos
    e assegura a rastreabilidade estrita da operação.
    """

    @staticmethod
    def list(
        company: Company, wedding_id: UUID | str | None = None
    ) -> QuerySet[Expense]:
        qs = Expense.objects.for_tenant(company).select_related(
            "category", "contract", "wedding"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Expense:
        try:
            return (
                Expense.objects.for_tenant(company)
                .select_related("category", "contract", "wedding")
                .get(uuid=uuid)
            )
        except Expense.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Despesa não encontrada.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Expense:
        logger.info(f"Iniciando criação de Despesa para company_id={company.id}")

        # 1. Resolução Segura de Categoria (Suporta Instância ou UUID)
        category_input = data.pop("category", None)

        if isinstance(category_input, BudgetCategory):
            category = category_input
        else:
            try:
                category = BudgetCategory.objects.for_tenant(company).get(
                    uuid=category_input
                )
            except BudgetCategory.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de categoria inválida/negada: {category_input}"
                )
                raise ObjectNotFoundError(
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
                    contract = Contract.objects.for_tenant(company).get(
                        uuid=contract_input
                    )
                except Contract.DoesNotExist as e:
                    logger.warning(
                        f"Tentativa de uso de contrato inválido/negado: "
                        f"{contract_input}"
                    )
                    raise ObjectNotFoundError(
                        detail="Contrato não encontrado ou acesso negado.",
                        code="contract_not_found_or_denied",
                    ) from e

        # 3. Injeção de Contexto (ADR-009) e Instanciação
        expense = Expense(
            company=company,
            wedding=category.wedding,
            category=category,
            contract=contract,
            **data,
        )

        # 4. Validação Estrita no Model
        try:
            expense.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao criar despesa para company_id=%s: %s",
                company.id,
                e,
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="expense_validation_error",
            ) from e

        logger.info(f"Despesa criada com sucesso: uuid={expense.uuid}")
        return expense

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Expense, data: dict[str, Any]) -> Expense:
        logger.info(
            f"Atualizando Despesa uuid={instance.uuid} por company_id={company.id}"
        )

        # Bloqueio de sequestro de contexto
        data.pop("company", None)
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
                        instance.contract = Contract.objects.for_tenant(company).get(
                            uuid=contract_input
                        )
                    except Contract.DoesNotExist as e:
                        raise ObjectNotFoundError(
                            detail="Contrato inválido ou acesso negado.",
                            code="contract_not_found_or_denied",
                        ) from e
            else:
                instance.contract = None

        # Atualização dinâmica dos campos
        for field, value in data.items():
            setattr(instance, field, value)

        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao atualizar despesa uuid=%s por company_id=%s: %s",
                instance.uuid,
                company.id,
                e,
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="expense_validation_error",
            ) from e

        logger.info(f"Despesa uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Expense) -> None:
        logger.info(
            f"Tentativa de deleção da Despesa uuid={instance.uuid} "
            f"por company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Despesa uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
            )

        except ProtectedError as e:
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
