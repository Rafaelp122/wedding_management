"""
Selectors de leitura para o domínio de contratos.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.core.exceptions import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.logistics.managers import ContractQuerySet
from apps.logistics.models import Contract
from apps.tenants.models import Company


if TYPE_CHECKING:
    from apps.weddings.models import Wedding


def contract_list_selector(
    company: Company,
    wedding_id: UUID | str | None = None,
    status: str | None = None,
    supplier_id: UUID | str | None = None,
    parent_id: UUID | str | None = None,
) -> ContractQuerySet:
    """
    Lista os contratos pertencentes ao tenant com filtros aplicados
    e anotações agregadas.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador do casamento para filtragem.
        status: Status do contrato (ex: DRAFT, SIGNED, PENDING, CANCELED).
        supplier_id: Identificador do fornecedor associado.
        parent_id: Identificador do contrato pai (aditivos).

    Returns:
        ContractQuerySet filtrado e anotado com totais e dados relacionados.
    """
    qs = cast(ContractQuerySet, Contract.objects.for_tenant(company)).with_totals()
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if status:
        qs = qs.by_status(status)
    if supplier_id:
        qs = qs.filter(supplier__uuid=supplier_id)
    if parent_id:
        qs = qs.filter(parent__uuid=parent_id)
    return qs


def contract_get_selector(company: Company, uuid: UUID | str) -> Contract:
    """
    Busca um contrato específico pertencente ao tenant com totais anotados.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único (UUID ou string) do contrato.

    Returns:
        A instância do Contract correspondente com dados e totais anotados.

    Raises:
        ObjectNotFoundError: Se o contrato não for encontrado ou
            não pertencer ao tenant.
    """
    try:
        return (
            cast(ContractQuerySet, Contract.objects.for_tenant(company))
            .with_totals()
            .get(uuid=uuid)
        )
    except (Contract.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(detail="Contrato não encontrado.") from e


def contract_pending_count_selector(
    company: Company,
    wedding_id: UUID | str | Wedding | None = None,
) -> int:
    """
    Retorna a contagem de contratos pendentes de assinatura para o tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para restringir a contagem.

    Returns:
        Número inteiro de contratos com status PENDING.
    """
    qs = cast(ContractQuerySet, Contract.objects.for_tenant(company)).by_status(
        Contract.StatusChoices.PENDING
    )
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs.count()
