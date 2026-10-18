"""Seletores de leitura para o domínio de Parcelas (Installment)."""

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
    exclude_paid: bool = False,
) -> InstallmentQuerySet:
    """
    Lista parcelas do tenant com filtros de status e intervalo de vencimento.

    Otimiza a leitura utilizando select_related para 'expense' e 'wedding' e
    aplica filtros especializados por status e datas (BR-F05).

    Returns:
        QuerySet de parcelas filtrado com relacionamentos pré-carregados.
    """
    qs: InstallmentQuerySet = Installment.objects.for_tenant(company).select_related(
        "expense", "wedding"
    )
    if expense_id:
        qs = qs.for_expense(expense_id)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if exclude_paid:
        qs = qs.exclude(status=Installment.StatusChoices.PAID)
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
    Recupera uma parcela pelo identificador único com relações pré-carregadas.

    Carrega 'expense' e 'wedding' via select_related garantindo o isolamento do tenant.

    Returns:
        A instância de parcela encontrada.

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
