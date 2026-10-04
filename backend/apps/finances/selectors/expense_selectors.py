"""Seletores de leitura para o domínio de Despesas (Expense)."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Expense


if TYPE_CHECKING:
    from apps.finances.managers import ExpenseQuerySet
    from apps.tenants.models import Company


def expense_list_selector(
    *,
    company: Company,
    wedding_id: UUID | str | None = None,
    category_id: UUID | str | None = None,
) -> ExpenseQuerySet:
    """
    Lista despesas do tenant com relacionamentos e agregações calculadas.

    Utiliza with_details() para carregar 'category', 'contract' e 'wedding' via
    select_related, além de anotar contagens e somas de parcelas pagas/pendentes.

    Returns:
        QuerySet de despesas filtrado e anotado com métricas de parcelamento.
    """
    qs: ExpenseQuerySet = Expense.objects.for_tenant(company).with_details()
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if category_id:
        qs = qs.by_category(category_id)
    return qs


def expense_get_selector(*, company: Company, uuid: UUID | str) -> Expense:
    """
    Recupera uma despesa por UUID com detalhes e métricas anotadas via with_details().

    Otimiza a leitura com select_related e agregações de parcelas. Suporta busca
    por UUID de parcela vinculada como fallback de conveniência.

    Returns:
        A instância de despesa com relacionamentos e métricas carregados.

    Raises:
        ObjectNotFoundError: Se a despesa não for encontrada ou não pertencer ao tenant.
    """
    try:
        return Expense.objects.for_tenant(company).with_details().get(uuid=uuid)
    except (Expense.DoesNotExist, ValueError, ValidationError) as e:
        from apps.finances.models import Installment

        installment = (
            Installment.objects.for_tenant(company)
            .filter(uuid=uuid)
            .select_related("expense")
            .first()
        )
        if installment and installment.expense:
            return (
                Expense.objects.for_tenant(company)
                .with_details()
                .get(pk=installment.expense_id)
            )

        raise ObjectNotFoundError(
            detail="Despesa não encontrada ou acesso negado.",
            code="expense_not_found_or_denied",
        ) from e
