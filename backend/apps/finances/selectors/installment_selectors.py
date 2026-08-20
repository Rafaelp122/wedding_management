"""
Selectors de leitura para o domínio de Parcelas (Installment).
Consultas otimizadas e encapsuladas de leitura para Installment.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.finances.models import Installment


if TYPE_CHECKING:
    from apps.finances.managers import InstallmentQuerySet
    from apps.tenants.models import Company


def installment_list_selector(
    *,
    company: Company,
    expense_id: UUID | str | None = None,
    wedding_id: UUID | str | None = None,
    status: str | None = None,
    due_date_gte: date | None = None,
    due_date_lte: date | None = None,
) -> InstallmentQuerySet:
    """
    Lista parcelas vinculadas ao tenant com filtros opcionais.

    Args:
        company: O tenant atual para isolamento de dados.
        expense_id: Identificador opcional da despesa pai.
        wedding_id: Identificador opcional do casamento.
        status: Status desejado (PENDING, PAID, OVERDUE).
        due_date_gte: Data de vencimento inicial para intervalo (inclusive).
        due_date_lte: Data de vencimento final para intervalo (inclusive).

    Returns:
        InstallmentQuerySet filtrado com relacionamentos pré-carregados.
    """
    qs: InstallmentQuerySet = Installment.objects.for_tenant(company).select_related(
        "expense", "wedding"
    )
    if expense_id:
        qs = qs.for_expense(expense_id)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if status:
        if status == Installment.StatusChoices.PENDING:
            qs = qs.pending()
        elif status == Installment.StatusChoices.PAID:
            qs = qs.paid()
        elif status == Installment.StatusChoices.OVERDUE:
            qs = qs.overdue()
        else:
            qs = qs.filter(status=status)
    if due_date_gte is not None or due_date_lte is not None:
        qs = qs.due_in_range(start_date=due_date_gte, end_date=due_date_lte)
    return qs


def installment_get_selector(*, company: Company, uuid: UUID | str) -> Installment:
    """
    Recupera uma parcela específica pelo UUID, garantindo isolamento multitenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único da parcela.

    Returns:
        A instância de Installment encontrada com expense e wedding carregados.

    Raises:
        ObjectNotFoundError: Se a parcela não existir ou pertencer a outro tenant.
    """
    return get_object_or_404_for_tenant(
        Installment,
        company,
        uuid,
        select_related=["expense", "wedding"],
        detail="Parcela não encontrada.",
        code="installment_not_found_or_denied",
    )
