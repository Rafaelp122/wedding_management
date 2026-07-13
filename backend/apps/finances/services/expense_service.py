import logging
from datetime import date
from typing import Any, cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.finances.managers import ExpenseQuerySet
from apps.finances.models import BudgetCategory, Expense
from apps.finances.schemas import ExpenseIn, ExpensePatchIn
from apps.finances.services.installment_service import InstallmentService
from apps.logistics.models import Contract
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


def _validate_contract_wedding(
    category: BudgetCategory, contract: Contract | None
) -> None:
    """Valida a fronteira cross-wedding entre categoria e contrato.

    Args:
        category: Categoria financeira que define o casamento da despesa.
        contract: Contrato logístico opcional vinculado à despesa.

    Raises:
        DomainIntegrityError: Se o contrato pertencer a outro casamento.
    """
    if contract and contract.wedding_id != category.wedding_id:
        raise DomainIntegrityError(
            detail=(
                "O contrato vinculado deve pertencer ao mesmo casamento da "
                "categoria de orçamento."
            ),
            code="expense_contract_wedding_mismatch",
        )


class ExpenseService:
    """Camada de serviço para orquestração de Despesas.

    Garante que gastos reais respeitem o contexto do casamento, os contratos
    e assegura a rastreabilidade estrita da operação.
    """

    @staticmethod
    def list(
        company: Company, wedding_id: UUID | str | None = None
    ) -> QuerySet[Expense]:
        """Lista despesas de uma empresa.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: UUID ou string do casamento para filtragem opcional.

        Returns:
            QuerySet[Expense]: QuerySet com as despesas filtradas e detalhadas.
        """
        qs = cast(ExpenseQuerySet, Expense.objects.for_tenant(company)).with_details()
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Expense:
        """Obtém uma despesa específica pelo seu UUID.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: O UUID da despesa desejada.

        Returns:
            Expense: A instância da despesa encontrada com detalhes.

        Raises:
            ObjectNotFoundError: Se a despesa não for encontrada.
        """
        # Nota: with_details() é um método do manager customizado.
        # get_object_or_404_for_tenant usa objects.for_tenant(company).
        # Para manter with_details(), vamos fazer manualmente ou garantir que
        # with_details() seja chamado no queryset.
        try:
            return (
                cast(ExpenseQuerySet, Expense.objects.for_tenant(company))
                .with_details()
                .get(uuid=uuid)
            )
        except (Expense.DoesNotExist, ValueError, ValidationError) as e:
            raise ObjectNotFoundError(
                detail="Despesa não encontrada ou acesso negado."
            ) from e

    @staticmethod
    def from_document(company: Company, contract_uuid: UUID | str) -> dict[str, Any]:
        """Prepara dados para criar despesa a partir de um contrato.

        Garante o preenchimento de campos obrigatórios com base nos valores
        do contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            contract_uuid: O UUID do contrato de origem.

        Returns:
            dict[str, Any]: Dicionário formatado contendo os dados sugeridos.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado.
        """
        contract = get_object_or_404_for_tenant(
            Contract,
            company,
            contract_uuid,
            select_related=["supplier"],
            code="contract_not_found_or_denied",
        )

        return {
            "name": (
                contract.name
                or contract.description
                or f"Despesa - {contract.supplier.name}"
            ),
            "description": contract.description or "",
            "contract": str(contract.uuid),
            "actual_amount": contract.total_amount,
            "category_uuid": None,
            "num_installments": None,
            "first_due_date": None,
        }

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ExpenseIn) -> Expense:
        """Cria uma nova despesa e gera suas parcelas correspondentes.

        Valida se o valor total da despesa é idêntico ao total do contrato
        associado (Regra BR-F02) e auto-gera pelo menos 1 parcela de pagamento.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação da despesa.

        Returns:
            Expense: A instância da despesa criada.

        Raises:
            BusinessRuleViolation: Se infringir a regra BR-F02 ou as parcelas
                forem inválidas.
        """
        logger.info(f"Iniciando criação de Despesa para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        category_input = data.pop("category", None)

        if isinstance(category_input, BudgetCategory):
            category = category_input
            validate_tenant_ownership(
                company,
                category,
                detail="Categoria de orçamento não encontrada ou acesso negado.",
                code="budget_category_not_found_or_denied",
            )
        else:
            category = get_object_or_404_for_tenant(
                BudgetCategory,
                company,
                category_input,
                detail="Categoria de orçamento não encontrada ou acesso negado.",
                code="budget_category_not_found_or_denied",
            )

        # 2. Resolução de Contrato (Opcional)
        contract = None
        contract_input = data.pop("contract", None)

        if contract_input:
            if isinstance(contract_input, Contract):
                contract = contract_input
                validate_tenant_ownership(
                    company,
                    contract,
                    detail="Contrato inválido ou acesso negado.",
                    code="contract_not_found_or_denied",
                )
            else:
                contract = get_object_or_404_for_tenant(
                    Contract,
                    company,
                    contract_input,
                    code="contract_not_found_or_denied",
                )

        _validate_contract_wedding(category, contract)

        num_installments = data.pop("num_installments", None)
        if num_installments is None:
            num_installments = 1
        first_due_date = data.pop("first_due_date", None) or date.today()

        if num_installments < 1:
            raise BusinessRuleViolation(
                detail="O número de parcelas deve ser pelo menos 1.",
                code="invalid_installment_number",
            )

        # BR-F02: snapshot inicial — despesa vinculada a contrato deve ter mesmo valor
        actual_amount = data.get("actual_amount")
        if contract and actual_amount and actual_amount != contract.total_amount:
            raise BusinessRuleViolation(
                detail=(
                    f"BR-F02: O valor da despesa (R${actual_amount}) "
                    f"deve ser igual ao valor do contrato "
                    f"(R${contract.total_amount})."
                ),
                code="br_f02_violation",
            )

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
                f"Falha de validação ao criar despesa para company_id={company.id}: {e}"
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="expense_validation_error",
            ) from e

        # 5. Geração automática de parcelas (mínimo 1)
        InstallmentService.auto_generate_installments(
            company=company,
            expense=expense,
            num_installments=num_installments,
            first_due_date=first_due_date,
        )

        logger.info(f"Despesa criada com sucesso: uuid={expense.uuid}")
        return expense

    @staticmethod
    def _validate_br_f02(instance: Expense, data: dict[str, Any]) -> None:
        """Valida a conformidade com a regra de negócio BR-F02.

        Garante que o valor da despesa vinculada a um contrato seja exatamente
        igual ao total do contrato.

        Args:
            instance: A instância da despesa sendo validada.
            data: Dicionário contendo os dados atualizados para validação.

        Raises:
            BusinessRuleViolation: Se o valor da despesa diferir do valor do contrato.
        """
        effective_contract = instance.contract
        effective_amount = data.get("actual_amount", instance.actual_amount)
        if effective_contract and effective_amount != effective_contract.total_amount:
            raise BusinessRuleViolation(
                detail=(
                    f"BR-F02: O valor da despesa (R${effective_amount}) "
                    f"deve ser igual ao valor do contrato "
                    f"(R${effective_contract.total_amount})."
                ),
                code="br_f02_violation",
            )

    @staticmethod
    def _resolve_contract(
        company: Company, instance: Expense, contract_input: Any
    ) -> None:
        """Resolve e vincula um contrato a uma despesa no update.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A despesa que receberá a vinculação do contrato.
            contract_input: Instância, UUID ou ID do contrato a ser resolvido.

        Raises:
            ObjectNotFoundError: Se o contrato especificado não for encontrado.
        """
        if contract_input:
            if isinstance(contract_input, Contract):
                instance.contract = contract_input
                validate_tenant_ownership(
                    company,
                    instance.contract,
                    detail="Contrato inválido ou acesso negado.",
                    code="contract_not_found_or_denied",
                )
            else:
                instance.contract = get_object_or_404_for_tenant(
                    Contract,
                    company,
                    contract_input,
                    code="contract_not_found_or_denied",
                    detail="Contrato inválido ou acesso negado.",
                )
        else:
            instance.contract = None

        if (
            instance.contract is not None
            and instance.contract.wedding_id != instance.wedding_id
        ):
            raise DomainIntegrityError(
                detail=(
                    "O contrato vinculado deve pertencer ao mesmo casamento da despesa."
                ),
                code="expense_contract_wedding_mismatch",
            )

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Expense, payload: ExpensePatchIn) -> Expense:
        """Atualiza os dados de uma despesa existente.

        Trata a re-distribuição de parcelas caso o valor total ou a quantidade de
        parcelas sejam alterados, validando a regra BR-F02 quando aplicável.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da despesa a ser atualizada.
            payload: Dados parciais de atualização da despesa.

        Returns:
            Expense: A instância da despesa atualizada.

        Raises:
            BusinessRuleViolation: Se a alteração de valor for bloqueada por parcelas
                já pagas ou se violar a consistência do model.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Despesa não encontrada ou acesso negado.",
            code="expense_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Despesa uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        contract_changed = "contract" in data
        if contract_changed:
            ExpenseService._resolve_contract(company, instance, data.pop("contract"))

        amount_changed = (
            "actual_amount" in data and data["actual_amount"] != instance.actual_amount
        )

        # BR-F02: validar somente se contract ou actual_amount estão sendo alterados
        if contract_changed or amount_changed:
            ExpenseService._validate_br_f02(instance, data)

        num_installments = data.pop("num_installments", None)
        first_due_date = data.pop("first_due_date", None)

        # Atualização dinâmica dos campos
        for field, value in data.items():
            setattr(instance, field, value)

        if amount_changed and num_installments is None:
            # Auto-redistribute: usa mesmo número de parcelas com novo valor
            if instance.installments.filter(status="PAID").exists():
                raise BusinessRuleViolation(
                    detail=(
                        "Não é possível alterar o valor total pois existem "
                        "parcelas marcadas como pagas. Crie uma nova despesa."
                    ),
                    code="amount_change_blocked_by_paid",
                )
            InstallmentService.redistribute(
                company=company,
                expense=instance,
                num_installments=instance.installments.count(),
                first_due_date=(
                    first_due_date
                    or getattr(
                        instance.installments.order_by("due_date").first(),
                        "due_date",
                        date.today(),
                    )
                ),
            )
        elif num_installments is not None:
            ExpenseService._handle_redistribute(
                company, instance, num_installments, first_due_date
            )

        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao atualizar despesa uuid={instance.uuid} "
                f"por company_id={company.id}: {e}"
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
        """Exclui uma despesa existente.

        Previamente valida a propriedade pelo tenant. Exclui a despesa e remove
        todas as parcelas vinculadas em cascata.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da despesa a ser excluída.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Despesa não encontrada ou acesso negado.",
            code="expense_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção da Despesa uuid={instance.uuid} "
            f"por company_id={company.id}"
        )

        instance.delete()
        logger.warning(
            f"Despesa uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
        )

    @staticmethod
    def _handle_redistribute(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date | None,
    ) -> None:
        """Gerencia o processo de redistribuição de parcelas de uma despesa.

        Args:
            company: O tenant atual para isolamento de dados.
            expense: A despesa associada que terá as parcelas redistribuídas.
            num_installments: Novo número total de parcelas.
            first_due_date: Data de vencimento da primeira parcela.

        Raises:
            BusinessRuleViolation: Se o número de parcelas for menor que 1.
        """
        if num_installments < 1:
            raise BusinessRuleViolation(
                detail="O número de parcelas deve ser pelo menos 1.",
                code="invalid_installment_number",
            )

        if first_due_date:
            first_due = first_due_date
        else:
            first_inst = expense.installments.order_by("due_date").first()
            first_due = first_inst.due_date if first_inst else date.today()

        InstallmentService.redistribute(
            company=company,
            expense=expense,
            num_installments=num_installments,
            first_due_date=first_due,
        )
