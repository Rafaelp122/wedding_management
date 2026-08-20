"""
Selectors de leitura para o domínio de Despesas (Expense).
Consultas otimizadas e encapsuladas de leitura para Expense.
"""

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
    Lista despesas vinculadas ao tenant com filtros opcionais.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para filtragem.
        category_id: Identificador opcional da categoria para filtragem.

    Returns:
        ExpenseQuerySet filtrado e anotado com contagens de parcelas
        e valores agregados.
    """
    qs: ExpenseQuerySet = Expense.objects.for_tenant(company).with_details()
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if category_id:
        qs = qs.by_category(category_id)
    return qs


def expense_get_selector(*, company: Company, uuid: UUID | str) -> Expense:
    """
    Recupera uma despesa específica pelo UUID, com detalhes anotados.
    Suporta busca por UUID de parcela vinculada como fallback de conveniência.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único da despesa (ou de uma parcela vinculada).

    Returns:
        A instância do Expense encontrada com detalhes e relacionamentos carregados.

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
