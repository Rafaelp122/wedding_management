"""
Seletores de leitura e agregação do Bounded Context de Contratos (apps.contracts).
"""

from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import Sum

from apps.contracts.managers import ContractAddendumQuerySet, ContractQuerySet
from apps.contracts.models import Contract, ContractAddendum
from apps.core.exceptions import ObjectNotFoundError
from apps.core.tenant import validate_tenant_ownership
from apps.tenants.models import Company


if TYPE_CHECKING:
    from apps.weddings.models import Wedding


def contract_list_selector(
    company: Company,
    wedding_id: UUID | str | None = None,
    status: str | None = None,
    contract_type: str | None = None,
    supplier_id: UUID | str | None = None,
    client_id: UUID | str | None = None,
    parent_id: UUID | str | None = None,
) -> ContractQuerySet:
    """Lista contratos do tenant aplicando filtros e otimizações de agregação.

    Aplica anotações de totais e pré-carregamento de termos aditivos (with_totals
    e prefetch_related), prevenindo problemas de performance N+1.

    Args:
        status: Status de contrato para filtragem (ex: DRAFT, SIGNED, PENDING, CANCELED).
        contract_type: Tipo de contrato para filtragem (PLANNER ou SUPPLIER).

    Returns:
        ContractQuerySet filtrado e anotado com totais e dados relacionados.
    """
    qs = (
        Contract.objects.for_tenant(company).with_totals().prefetch_related("addendums")
    )
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if status:
        qs = qs.by_status(status)
    if contract_type:
        qs = qs.by_type(contract_type)
    if supplier_id:
        qs = qs.filter(supplier__uuid=supplier_id)
    if client_id:
        qs = qs.filter(client__uuid=client_id)
    if parent_id:
        return qs.none()
    return qs


def contract_get_selector(company: Company, uuid: UUID | str) -> Contract:
    """Busca um contrato específico pertencente ao tenant com totais anotados.

    Executa consulta com cálculo de totais via subquery e pré-carregamento de aditivos
    (with_totals e prefetch_related), garantindo eficiência de I/O.

    Returns:
        A instância do Contract correspondente com dados e totais anotados.

    Raises:
        ObjectNotFoundError: Se o contrato não for encontrado ou pertencer a outro tenant.
    """
    try:
        return (
            Contract.objects.for_tenant(company)
            .with_totals()
            .prefetch_related("addendums")
            .get(uuid=uuid)
        )
    except (Contract.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(detail="Contrato não encontrado.") from e


def contract_pending_count_selector(
    company: Company,
    wedding_id: UUID | str | Wedding | None = None,
) -> int:
    """Retorna a contagem de contratos pendentes de assinatura para o tenant.

    Returns:
        Número total de contratos com status PENDING.
    """
    qs = Contract.objects.for_tenant(company).by_status(Contract.StatusChoices.PENDING)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs.count()


def contract_consolidated_total_selector(
    company: Company,
    contract: Contract,
) -> Decimal:
    """Calcula o valor efetivo consolidado do contrato (face + aditivos SIGNED).

    Regra de Negócio:
        BR-L02-E (docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)

    Executa agregação pontual filtrando exclusivamente aditivos assinados. Aditivos
    PENDING e CANCELED não compõem o montante liquidável.

    Returns:
        Montante consolidado somando o valor de face aos aditivos assinados.
    """
    validate_tenant_ownership(
        company,
        contract,
        detail="Contrato não encontrado ou acesso negado.",
        code="contract_not_found_or_denied",
    )
    addendums_sum = (
        contract.addendums.for_tenant(company)
        .filter(status=ContractAddendum.StatusChoices.SIGNED)
        .aggregate(total=Sum("amount"))["total"]
    )
    return (contract.total_amount or Decimal("0.00")) + (
        addendums_sum or Decimal("0.00")
    )


def contract_detail_aggregate_selector(
    *,
    company: Company,
    contract_uuid: UUID | str,
) -> dict[str, Any]:
    """Busca o contrato com totais anotados, seus itens associados e termos aditivos.

    Aplica select_related para entidades principais (wedding, supplier, client)
    e prefetch_related para coleções filhas (addendums, items) para otimização de queries.

    Returns:
        Dicionário agregando o contrato com totais, itens e aditivos.

    Raises:
        ObjectNotFoundError: Se o contrato não for encontrado ou pertencer a outro tenant.
    """
    try:
        qs = (
            Contract.objects.for_tenant(company)
            .with_totals()
            .select_related("wedding", "supplier", "client")
            .prefetch_related("addendums", "items")
        )
        contract = qs.get(uuid=contract_uuid)
    except (Contract.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(detail="Contrato não encontrado.") from e

    items_list = list(contract.items.all())

    return {
        "contract": contract,
        "items": items_list,
        "addendums": list(contract.addendums.all()),
    }


def contract_addendum_list_selector(
    company: Company,
    contract_uuid: UUID | str,
) -> ContractAddendumQuerySet:
    """Lista todos os termos aditivos pertencentes a um contrato.

    Aplica select_related para o contrato principal e ordena por criação decrescente.

    Returns:
        ContractAddendumQuerySet com os termos aditivos do contrato.
    """
    return (
        ContractAddendum.objects.for_tenant(company)
        .filter(contract__uuid=contract_uuid)
        .select_related("contract")
        .order_by("-created_at")
    )


def contract_addendum_get_selector(
    company: Company,
    contract_uuid: UUID | str,
    addendum_uuid: UUID | str,
) -> ContractAddendum:
    """Busca um termo aditivo específico validando posse e pertinência ao contrato.

    Carrega a relação do contrato principal via select_related.

    Returns:
        A instância do aditivo correspondente.

    Raises:
        ObjectNotFoundError: Se o aditivo não existir ou pertencer a outro tenant/contrato.
    """
    try:
        addendum: ContractAddendum = (
            ContractAddendum.objects.for_tenant(company)
            .select_related("contract")
            .get(uuid=addendum_uuid, contract__uuid=contract_uuid)
        )
        return addendum
    except (ContractAddendum.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(detail="Termo aditivo não encontrado.") from e
