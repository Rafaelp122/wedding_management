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
    """Lista os contratos pertencentes ao tenant com filtros aplicados.

    Retorna o QuerySet anotado com totais e dados consolidados evitando N+1.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador do casamento para filtragem.
        status: Status do contrato (ex: DRAFT, SIGNED, PENDING, CANCELED).
        contract_type: Tipo do contrato (PLANNER ou SUPPLIER).
        supplier_id: Identificador do fornecedor associado.
        client_id: Identificador do cliente contratante associado.
        parent_id: Parâmetro legado mantido para compatibilidade de rotas.

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

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: Identificador único (UUID ou string) do contrato.

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

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para restringir a contagem.

    Returns:
        Número inteiro de contratos com status PENDING.
    """
    qs = Contract.objects.for_tenant(company).by_status(Contract.StatusChoices.PENDING)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs.count()


def contract_consolidated_total_selector(
    company: Company,
    contract: Contract,
) -> Decimal:
    """Calcula o valor efetivo do contrato (face + aditivos SIGNED).

    SSOT de valor formalizado: somente aditivos SIGNED compõem o total.
    Aditivos PENDING são expectativa futura (ver `addendums_pending_total`
    em `with_totals()`) e CANCELED nunca compõem.

    Args:
        company: O tenant atual para isolamento de dados.
        contract: Instância do contrato a ser calculado.

    Returns:
        Decimal com a soma do valor de face mais aditivos assinados.
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

    Args:
        company: O tenant atual para isolamento de dados.
        contract_uuid: Identificador único do contrato.

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

    Args:
        company: O tenant atual para isolamento de dados.
        contract_uuid: Identificador do contrato principal.

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

    Args:
        company: O tenant atual para isolamento de dados.
        contract_uuid: Identificador do contrato principal.
        addendum_uuid: Identificador único do aditivo.

    Returns:
        Instância do aditivo correspondente.

    Raises:
        ObjectNotFoundError: Se o aditivo não existir ou pertencer a outro tenant/contrato.
    """
    try:
        return (
            ContractAddendum.objects.for_tenant(company)
            .select_related("contract")
            .get(uuid=addendum_uuid, contract__uuid=contract_uuid)
        )
    except (ContractAddendum.DoesNotExist, ValueError, ValidationError) as e:
        raise ObjectNotFoundError(detail="Termo aditivo não encontrado.") from e
