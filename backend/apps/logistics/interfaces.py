"""
Fachada pública (Interface) do Bounded Context de Logística.
Centraliza operações síncronas invocadas por outros contextos (ex: finances, contracts).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID


if TYPE_CHECKING:
    from apps.tenants.models import Company


def create_item_for_contract(
    *,
    company: Company,
    payload: Any,
    contract_uuid: UUID | str | None = None,
    wedding_uuid: UUID | str | None = None,
) -> Any:
    """Cria um item de suprimento vinculado a um contrato.

    Args:
        company: O tenant atual para isolamento de dados.
        payload: Schema de entrada com os dados do item.
        contract_uuid: UUID do contrato ao qual o item será associado.
        wedding_uuid: UUID do casamento ao qual o item será associado.

    Returns:
        Instância do item criado.
    """
    from apps.logistics.schemas import ItemIn
    from apps.logistics.services.item_service import ItemService

    if isinstance(payload, ItemIn):
        data = payload.model_dump()
    elif hasattr(payload, "model_dump"):
        data = payload.model_dump()
    elif hasattr(payload, "dict"):
        data = payload.dict()
    elif isinstance(payload, dict):
        data = payload.copy()
    else:
        data = {
            "name": getattr(payload, "name", ""),
            "quantity": getattr(payload, "quantity", 1),
            "description": getattr(payload, "description", ""),
        }

    raw_c = contract_uuid or data.get("contract")
    raw_w = wedding_uuid or data.get("wedding")
    c_uuid = UUID(str(raw_c)) if raw_c else None
    w_uuid = UUID(str(raw_w)) if raw_w else None
    item_in = ItemIn(
        name=data["name"],
        quantity=data.get("quantity", 1),
        description=data.get("description", ""),
        contract=c_uuid,
        wedding=w_uuid,
    )
    return ItemService.create(company=company, payload=item_in)


__all__ = [
    "create_item_for_contract",
]
