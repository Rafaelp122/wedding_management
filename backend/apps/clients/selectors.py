"""
Selectors de leitura para o domínio de clientes (CQRS).
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from django.db.models import QuerySet

from apps.clients.models import Client
from apps.core.shortcuts import get_object_or_404_for_tenant


if TYPE_CHECKING:
    from apps.tenants.models import Company


def client_list_selector(
    company: Company,
    q: str = "",
) -> QuerySet[Client]:
    """
    Retorna a listagem de clientes do tenant com suporte a busca textual.

    Args:
        company: O tenant atual para isolamento de dados.
        q: Termo opcional para busca textual em nome, CPF, e-mail ou telefone.

    Returns:
        QuerySet de instâncias de Client ordenadas por nome.
    """
    qs = Client.objects.for_tenant(company)
    if q:
        qs = qs.search(q)
    return qs.order_by("name")


def client_get_selector(
    company: Company,
    uuid: UUID | str,
) -> Client:
    """
    Recupera um cliente específico pelo identificador público (UUID).

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único público do cliente.

    Returns:
        A instância de Client encontrada e pertencente à empresa.

    Raises:
        ObjectNotFoundError: Se o cliente não existir ou pertencer a outro tenant.
    """
    return get_object_or_404_for_tenant(Client, company, uuid=uuid)
