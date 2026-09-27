"""
Fachada pública (Interface) do Bounded Context de Finanças.
Centraliza operações síncronas invocadas por outros contextos (ex: logistics, weddings).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from django.utils import timezone

from apps.core.shortcuts import resolve_tenant_resource
from apps.finances.models import Budget, BudgetCategory
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService


if TYPE_CHECKING:
    from apps.finances.models import Expense
    from apps.tenants.models import Company


def create_expense_from_contract(
    *,
    company: Company,
    payload: ExpenseIn,
    contract_uuid: UUID | str,
) -> Expense:
    """
    Cria uma despesa vinculada a um contrato logístico.

    Args:
        company: Tenant para isolamento de dados.
        payload: Dados da despesa informados.
        contract_uuid: Identificador único do contrato a ser vinculado.

    Returns:
        A instância de Expense criada e persistida.
    """
    expense_payload = payload.model_copy(update={"contract": contract_uuid})
    return ExpenseService.create(company=company, payload=expense_payload)


def create_expense_from_planner_contract(
    *,
    company: Company,
    wedding: Any,
    planner_contract: Any,
    category_id: UUID | str | None = None,
) -> Expense:
    """
    Cria uma despesa e suas parcelas a partir do contrato de assessoria cerimonial.

    Garante a existência do orçamento mestre e da categoria 'Assessoria',
    alocando a verba e lançando a despesa com tolerância zero (BR-F01/BR-F04).

    Args:
        company: Tenant para isolamento de dados.
        wedding: Instância do casamento associado.
        planner_contract: Instância do Contract com honorários e parcelamento.
        category_id: Categoria orçamentária opcional; se omitida, busca ou cria 'Assessoria'.

    Returns:
        A instância de Expense criada e persistida com suas parcelas.
    """
    fee = getattr(
        planner_contract,
        "total_amount",
        getattr(planner_contract, "effective_amount", Decimal("0.00")),
    )
    category: BudgetCategory

    if category_id is not None:
        category = resolve_tenant_resource(
            BudgetCategory,
            company,
            category_id,
            detail="Categoria de orçamento não encontrada ou acesso negado.",
            code="budget_category_not_found_or_denied",
        )
        budget = category.budget
    else:
        existing_budget = Budget.objects.filter(
            company=company, wedding=wedding
        ).first()
        if not existing_budget:
            budget = Budget(
                company=company,
                wedding=wedding,
                total_estimated=max(Decimal("0.00"), fee),
                notes="Orçamento mestre gerado na formalização do contrato de assessoria.",
            )
            budget.freeze_baseline()
            budget.save()
        else:
            budget = existing_budget
            if budget.total_estimated < budget.total_allocated + fee:
                budget.total_estimated = budget.total_allocated + fee
                budget.save(update_fields=["total_estimated", "updated_at"])

        cat = BudgetCategory.objects.filter(
            company=company, budget=budget, name__iexact="Assessoria"
        ).first()
        if not cat:
            cat = BudgetCategory(
                company=company,
                budget=budget,
                wedding=wedding,
                name="Assessoria",
                description="Honorários da assessoria cerimonial",
                allocated_budget=fee,
            )
            cat.save()
        elif cat.allocated_budget < fee:
            cat.allocated_budget = fee
            cat.save(update_fields=["allocated_budget", "updated_at"])
        category = cat

    if budget:
        budget.freeze_baseline()
        budget.save(update_fields=["baseline_amount", "updated_at"])

    tier_label = (
        planner_contract.get_service_tier_display()
        if hasattr(planner_contract, "get_service_tier_display")
        else planner_contract.service_tier
    )
    first_due_date = planner_contract.signed_date or timezone.now().date()
    contract_uuid = getattr(planner_contract, "uuid", None)

    expense_payload = ExpenseIn(
        category=category.uuid,
        contract=contract_uuid,
        name=f"Honorários de Assessoria ({tier_label})",
        description=f"Honorários do contrato de assessoria cerimonial ({planner_contract.service_tier})",
        estimated_amount=fee,
        actual_amount=fee,
        num_installments=planner_contract.installments_count,
        first_due_date=first_due_date,
    )
    return ExpenseService.create(company=company, payload=expense_payload)


def add_expense_adjustment_from_addendum(
    company: Company,
    contract_uuid: UUID | str,
    addendum_amount: Decimal | float | str,
) -> Expense | None:
    """
    Ajusta o montante da despesa vinculada a um contrato após a formalização de um aditivo.

    Atualiza actual_amount somando o valor do aditivo e preserva a regra de Tolerância Zero
    (BR-F01/ADR-010) gerando uma nova parcela para o aditivo caso já existam parcelas.

    Args:
        company: O tenant atual para isolamento multitenant.
        contract_uuid: Identificador único (UUID ou string) do contrato principal.
        addendum_amount: Valor do aditivo a ser acrescido na despesa.

    Returns:
        A instância de Expense atualizada, ou None caso o contrato não possua despesa vinculada.
    """
    from datetime import timedelta

    from django.db import transaction

    from apps.finances.models import Expense, Installment
    from apps.scheduler.interfaces import create_payment_events_for_installments

    amount = Decimal(str(addendum_amount))

    with transaction.atomic():
        expense = (
            Expense.objects.select_for_update()
            .filter(company=company, contract__uuid=contract_uuid)
            .first()
        )
        if not expense and str(contract_uuid).isdigit():
            expense = (
                Expense.objects.select_for_update()
                .filter(company=company, contract_id=int(contract_uuid))
                .first()
            )

        if not expense:
            return None

        if expense.installments.exists():
            last_inst = expense.installments.order_by("-installment_number").first()
            next_num = (last_inst.installment_number + 1) if last_inst else 1
            last_due = last_inst.due_date if last_inst else timezone.now().date()
            next_due = last_due + timedelta(days=30)

            adjustment_inst = Installment(
                company=company,
                wedding=expense.wedding,
                expense=expense,
                installment_number=next_num,
                amount=amount,
                due_date=next_due,
                status=Installment.StatusChoices.PENDING,
                notes="Ajuste referente a termo aditivo formalizado",
            )
            adjustment_inst.save()

            transaction.on_commit(
                lambda: create_payment_events_for_installments(
                    company=company, expense=expense, installments=[adjustment_inst]
                )
            )

        expense.actual_amount += amount

        expense.save(update_fields=["actual_amount", "updated_at"])
        return expense


def freeze_budget_baseline_for_wedding(
    company: Company,
    wedding: Any,
) -> None:
    """
    Congela a linha de base original do orçamento mestre para o casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: Instância do casamento associado.
    """
    budget = Budget.objects.filter(company=company, wedding=wedding).first()
    if budget:
        budget.freeze_baseline()
        budget.save(update_fields=["baseline_amount", "updated_at"])


__all__ = [
    "ExpenseIn",
    "add_expense_adjustment_from_addendum",
    "create_expense_from_contract",
    "create_expense_from_planner_contract",
    "freeze_budget_baseline_for_wedding",
]
