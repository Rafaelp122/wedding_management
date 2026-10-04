import logging
from datetime import date
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.contracts.interfaces import get_contract_for_company
from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import BudgetCategory, Expense
from apps.finances.schemas import ExpenseIn, ExpensePatchIn
from apps.finances.services.installment_service import InstallmentService
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class ExpenseService:
    """Camada de serviço para mutações e orquestração de Despesas.

    Garante que gastos reais respeitem o contexto do casamento, os contratos
    e assegura a rastreabilidade estrita da operação.

    Regras de Negócio:
        BR-F01 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
        BR-F02 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
        BR-F03 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
        BR-F04 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
    """

    @staticmethod
    def _validate_contract_wedding(category: BudgetCategory, contract: Any) -> None:
        """Valida a fronteira cross-wedding entre categoria e contrato.

        Raises:
            DomainIntegrityError: Se o contrato pertencer a outro casamento (BR-F03).
        """
        if contract and contract.wedding_id != category.wedding_id:
            raise DomainIntegrityError(
                detail=(
                    "O contrato vinculado deve pertencer ao mesmo casamento da "
                    "categoria de orçamento."
                ),
                code="expense_contract_wedding_mismatch",
            )

    @staticmethod
    def from_document(company: Company, contract_uuid: UUID | str) -> dict[str, Any]:
        """Prepara dados para criar despesa a partir de um contrato.

        Garante o preenchimento de campos obrigatórios com base nos valores
        do contrato.

        Returns:
            Dicionário formatado contendo os dados sugeridos para a despesa.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado ou não pertencer ao tenant.
        """
        contract = get_contract_for_company(
            company=company,
            contract_uuid_or_id=contract_uuid,
            select_related=["supplier"],
        )

        return {
            "name": (
                contract.name
                or contract.description
                or (
                    f"Despesa - {contract.supplier.name}"
                    if contract.supplier
                    else "Despesa de Contrato"
                )
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

        Regras de Negócio:
            BR-F01 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
            BR-F02 (docs/architecture/business-rules/finances/financial-integrity-rules.md)
            BR-F03 (docs/architecture/business-rules/finances/financial-integrity-rules.md)

        Efeitos Colaterais:
            - Persiste atomicamente a despesa e gera suas parcelas via InstallmentService.

        Returns:
            A instância de despesa criada.

        Raises:
            BusinessRuleViolation: Se infringir a regra BR-F02, se o número de parcelas
                for inválido (< 1) ou se violar validações do modelo.
            DomainIntegrityError: Se o contrato pertencer a outro casamento (BR-F03).
            ObjectNotFoundError: Se a categoria de orçamento não for encontrada.
        """
        logger.info(f"Iniciando criação de Despesa para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        category_input = data.pop("category", None)

        category = resolve_tenant_resource(
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
            contract = get_contract_for_company(
                company=company,
                contract_uuid_or_id=contract_input,
            )

        ExpenseService._validate_contract_wedding(category, contract)

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

        Raises:
            BusinessRuleViolation: Se o valor da despesa diferir do valor do contrato (BR-F02).
        """
        effective_contract = instance.contract
        effective_amount = data.get("actual_amount", instance.actual_amount)
        if effective_contract:
            expected_amount = getattr(
                effective_contract, "effective_amount", effective_contract.total_amount
            )
            if effective_amount != expected_amount:
                raise BusinessRuleViolation(
                    detail=(
                        f"BR-F02: O valor da despesa (R${effective_amount}) "
                        f"deve ser igual ao valor do contrato "
                        f"(R${expected_amount})."
                    ),
                    code="br_f02_violation",
                )

    @staticmethod
    def _resolve_contract(
        company: Company, instance: Expense, contract_input: Any
    ) -> None:
        """Resolve e vincula um contrato a uma despesa no update.

        Raises:
            DomainIntegrityError: Se o contrato pertencer a outro casamento (BR-F03).
            ObjectNotFoundError: Se o contrato especificado não for encontrado.
        """
        resolved_contract = None
        if contract_input:
            resolved_contract = get_contract_for_company(
                company=company,
                contract_uuid_or_id=contract_input,
            )

        if (
            resolved_contract is not None
            and resolved_contract.wedding_id != instance.wedding_id
        ):
            raise DomainIntegrityError(
                detail=(
                    "O contrato vinculado deve pertencer ao mesmo casamento da despesa."
                ),
                code="expense_contract_wedding_mismatch",
            )

        instance.contract = resolved_contract

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Expense, payload: ExpensePatchIn) -> Expense:
        """Atualiza os dados de uma despesa existente.

        Trata a redistribuição de parcelas caso o valor total seja alterado,
        validando a regra BR-F02 quando aplicável.

        Efeitos Colaterais:
            - Atualiza a despesa e redistribui proporcionalmente as parcelas em caso de alteração no valor total (BR-F01).

        Returns:
            A instância de despesa atualizada.

        Raises:
            BusinessRuleViolation: Se a alteração de valor for bloqueada por parcelas
                já pagas (BR-F04), violar a paridade contratual (BR-F02) ou quebrar consistência do modelo.
            DomainIntegrityError: Se o novo contrato pertencer a outro casamento (BR-F03).
            ObjectNotFoundError: Se o novo contrato especificado não for encontrado.
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

        updated_fields: set[str] = set()
        data = payload.model_dump(exclude_unset=True)

        contract_changed = "contract" in data
        if contract_changed:
            ExpenseService._resolve_contract(company, instance, data.pop("contract"))
            updated_fields.add("contract")

        amount_changed = (
            "actual_amount" in data and data["actual_amount"] != instance.actual_amount
        )

        # BR-F02: validar somente se contract ou actual_amount estão sendo alterados
        if contract_changed or amount_changed:
            ExpenseService._validate_br_f02(instance, data)

        # Atualização dinâmica dos campos
        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if amount_changed:
            # Auto-redistribute: ajusta o valor das parcelas existentes
            # para o novo valor total (BR-F01)
            if instance.has_paid_installments:
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
                first_due_date=(instance.first_due_date or date.today()),
            )

        if updated_fields:
            updated_fields.add("updated_at")
            try:
                instance.save(update_fields=list(updated_fields))
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

        Efeitos Colaterais:
            - Remove a despesa e suas parcelas associadas em cascata.
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
    @transaction.atomic
    def renegotiate_installments(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date | None = None,
    ) -> Expense:
        """Renegocia e redistribui as parcelas de uma despesa.

        Remove as parcelas anteriores e gera um novo cronograma com a quantidade
        de parcelas informada e data de primeiro vencimento.

        Efeitos Colaterais:
            - Exclui as parcelas pendentes anteriores e gera um novo cronograma balanceado (BR-F01).

        Args:
            num_installments: Novo número total de parcelas (deve ser >= 1).
            first_due_date: Data base para vencimento da primeira parcela (opcional).

        Returns:
            A despesa com as parcelas renegociadas.

        Raises:
            BusinessRuleViolation: Se o número de parcelas for menor que 1 ou
                se houver parcelas já pagas (BR-F04).
        """
        validate_tenant_ownership(company, expense)

        if num_installments < 1:
            raise BusinessRuleViolation(
                detail="O número de parcelas deve ser pelo menos 1.",
                code="invalid_installment_number",
            )

        first_due = first_due_date or expense.first_due_date or date.today()

        InstallmentService.redistribute(
            company=company,
            expense=expense,
            num_installments=num_installments,
            first_due_date=first_due,
        )
        return expense
