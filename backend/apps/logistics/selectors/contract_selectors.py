from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db.models import Sum

from apps.core.exceptions import ObjectNotFoundError
from apps.core.tenant import validate_tenant_ownership
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
    qs = Contract.objects.for_tenant(company).with_totals()
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
        return Contract.objects.for_tenant(company).with_totals().get(uuid=uuid)
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
    qs = Contract.objects.for_tenant(company).by_status(Contract.StatusChoices.PENDING)
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    return qs.count()


def contract_consolidated_total_selector(
    company: Company,
    contract: Contract,
) -> Decimal:
    """
    Calcula o valor total consolidado de um contrato somado aos seus
    aditivos ativos para um tenant.

    Exclui termos aditivos com status CANCELED.

    Args:
        company: O tenant atual para isolamento de dados.
        contract: Instância do contrato a ser calculado.

    Returns:
        Decimal com a soma do valor de face do contrato mais seus
        aditivos ativos.

    Raises:
        ObjectNotFoundError: Se o contrato não pertencer ao tenant.
    """
    validate_tenant_ownership(
        company,
        contract,
        detail="Contrato não encontrado ou acesso negado.",
        code="contract_not_found_or_denied",
    )
    addendums_sum = (
        contract.addendums.for_tenant(company)
        .exclude(status=Contract.StatusChoices.CANCELED)
        .aggregate(total=Sum("total_amount"))["total"]
    )
    return (contract.total_amount or Decimal("0.00")) + (
        addendums_sum or Decimal("0.00")
    )
