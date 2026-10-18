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
    """Cria uma despesa vinculada a um contrato logístico.

    Regra de Negócio:
        BR-F02 (docs/architecture/business-rules/finances/financial-integrity-rules.md)

    Efeitos Colaterais:
        - Delega ao ExpenseService a persistência atômica da despesa e parcelas.
    """
    expense_payload = payload.model_copy(update={"contract": contract_uuid})
    return ExpenseService.create(company=company, payload=expense_payload)


def _ensure_planner_budget(company: Company, wedding: Any, fee: Decimal) -> Budget:
    """Garante a existência do orçamento mestre com teto adequado aos honorários."""
    budget = Budget.objects.filter(company=company, wedding=wedding).first()
    if not budget:
        budget = Budget(
            company=company,
            wedding=wedding,
            total_estimated=max(Decimal("0.00"), fee),
            notes="Orçamento mestre gerado na formalização do contrato de assessoria.",
        )
        budget.freeze_baseline()
        budget.save()
        return budget

    if budget.total_estimated < budget.total_allocated + fee:
        budget.total_estimated = budget.total_allocated + fee
        budget.save(update_fields=["total_estimated", "updated_at"])
    return budget


def _ensure_planner_category(
    company: Company, wedding: Any, budget: Budget, fee: Decimal
) -> BudgetCategory:
    """Garante a categoria 'Assessoria' com alocação compatível aos honorários."""
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
        return cat

    if cat.allocated_budget < fee:
        cat.allocated_budget = fee
        cat.save(update_fields=["allocated_budget", "updated_at"])
    return cat


def create_expense_from_planner_contract(
    *,
    company: Company,
    wedding: Any,
    planner_contract: Any,
    category_id: UUID | str | None = None,
) -> Expense:
    """Cria despesa e parcelas a partir do contrato de assessoria cerimonial.

    Regra de Negócio:
        BR-F01 (docs/architecture/business-rules/finances/financial-integrity-rules.md)

    Efeitos Colaterais:
        - Cria ou atualiza o orçamento mestre e a categoria 'Assessoria'.
        - Persiste a despesa e suas parcelas via ExpenseService.
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
        budget = _ensure_planner_budget(company, wedding, fee)
        category = _ensure_planner_category(company, wedding, budget, fee)

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
    """Ajusta o montante da despesa vinculada a um contrato após aditivo.

    Regra de Negócio:
        BR-F01 (docs/architecture/business-rules/finances/financial-integrity-rules.md)

    Efeitos Colaterais:
        - Persiste nova parcela com valor do aditivo sob lock pessimista no banco.
        - Enfileira no commit a criação de evento PAYMENT na agenda (BR-S01-SYNC).
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
    """Congela a linha de base original do orçamento mestre para o casamento.

    Regra de Negócio:
        BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

    Efeitos Colaterais:
        - Atualiza o campo baseline_amount do orçamento mestre caso ainda não congelado.
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
