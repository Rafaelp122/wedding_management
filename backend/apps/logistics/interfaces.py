"""
Fachada pública (Interface) do Bounded Context de Logística.
Centraliza operações síncronas invocadas por outros contextos (ex: finances).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import resolve_tenant_resource
from apps.logistics.models import Contract


if TYPE_CHECKING:
    from apps.tenants.models import Company


def get_contract_for_company(
    *,
    company: Company,
    contract_uuid_or_id: UUID | str | Contract,
    select_related: list[str] | None = None,
) -> Contract:
    """
    Recupera uma instância de Contract validando a posse pelo tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        contract_uuid_or_id: UUID, ID inteiro ou instância de Contract.
        select_related: Relacionamentos adicionais a carregar via JOIN.

    Returns:
        Instância de Contract validada e pertencente ao tenant.
    """
    return resolve_tenant_resource(
        Contract,
        company,
        contract_uuid_or_id,
        select_related=select_related,
        detail="Contrato inválido ou acesso negado.",
        code="contract_not_found_or_denied",
    )


__all__ = [
    "get_contract_for_company",
]
