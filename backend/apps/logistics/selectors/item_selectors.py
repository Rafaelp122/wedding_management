from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.logistics.managers import ItemQuerySet
from apps.logistics.models import Item
from apps.tenants.models import Company


if TYPE_CHECKING:
    from apps.logistics.models import Contract
    from apps.weddings.models import Wedding


def item_list_selector(
    company: Company,
    wedding_id: UUID | str | Wedding | None = None,
    status: str | None = None,
    search: str | None = None,
    contract_id: UUID | str | Contract | None = None,
) -> ItemQuerySet:
    """
    Lista os itens de logística pertencentes ao tenant com filtros aplicados.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador único do casamento ou instância de Wedding.
        status: Status de aquisição do item (ex: PENDING, IN_PROGRESS, DONE).
        search: Termo para busca parcial no nome do item.
        contract_id: Identificador único do contrato associado ou instância de Contract.

    Returns:
        ItemQuerySet contendo os itens filtrados com relacionamentos carregados.
    """
    qs = Item.objects.for_tenant(company).with_details()
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if status:
        qs = qs.by_status(status)
    if search:
        qs = qs.search(search)
    if contract_id:
        qs = qs.for_contract(contract_id)
    return qs


def item_get_selector(company: Company, uuid: UUID | str) -> Item:
    """
    Recupera um item de logística específico pelo UUID com isolamento por tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único (UUID ou string) do item.

    Returns:
        A instância do Item correspondente com relacionamentos carregados.

    Raises:
        ObjectNotFoundError: Se o item não for encontrado ou não pertencer ao tenant.
    """
    return get_object_or_404_for_tenant(
        Item,
        company,
        uuid,
        select_related=["wedding", "contract", "contract__supplier"],
        detail="Item de logística não encontrado.",
    )
