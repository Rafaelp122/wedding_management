"""
Fachada pública (Interface) do Bounded Context de Finanças.
Centraliza operações síncronas invocadas por outros contextos (ex: logistics).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

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


__all__ = [
    "ExpenseIn",
    "create_expense_from_contract",
]
