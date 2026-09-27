"""
Fachada pública (Interface) do Bounded Context de Contratos e Termos Aditivos.

Centraliza operações síncronas invocadas por outros contextos (ADR-031),
como finanças, logística e casamentos.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError

from apps.contracts.models import Contract
from apps.core.exceptions import BusinessRuleViolation
from apps.core.shortcuts import resolve_tenant_resource
from apps.suppliers.interfaces import get_supplier_for_company


if TYPE_CHECKING:
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding


def get_contract_for_company(
    *,
    company: Company,
    contract_uuid_or_id: UUID | str | Contract,
    select_related: list[str] | None = None,
) -> Contract:
    """Recupera uma instância de Contract validando a posse pelo tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        contract_uuid_or_id: UUID, ID numérico ou instância de Contract.
        select_related: Lista de relações adicionais para otimização de JOIN.

    Returns:
        Instância de Contract pertencente à empresa tenant.
    """
    return resolve_tenant_resource(
        Contract,
        company,
        contract_uuid_or_id,
        select_related=select_related,
        detail="Contrato inválido ou acesso negado.",
        code="contract_not_found_or_denied",
    )


def list_contracts_for_wedding(
    *,
    company: Company,
    wedding_uuid: UUID | str,
    contract_type: str | None = None,
) -> list[Contract]:
    """Lista todos os contratos vinculados a um casamento para um determinado tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_uuid: Identificador único do casamento.
        contract_type: Filtro opcional por tipo de contrato (ex: PLANNER, SUPPLIER).

    Returns:
        Lista de contratos ordenados por nome.
    """
    qs = Contract.objects.for_tenant(company).filter(wedding__uuid=wedding_uuid)
    if contract_type:
        qs = qs.filter(contract_type=contract_type)
    return list(qs.order_by("name"))


def get_planner_contract_for_wedding(
    *,
    company: Company,
    wedding: Wedding,
) -> Contract | None:
    """Retorna o contrato de honorários da assessoria (PLANNER) do casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: Instância do casamento associado.

    Returns:
        Instância de Contract do tipo PLANNER ou None se ainda não cadastrado.
    """
    return (
        Contract.objects.for_tenant(company)
        .filter(wedding=wedding, contract_type=Contract.ContractTypeChoices.PLANNER)
        .first()
    )


def save_planner_contract_for_wedding(
    *,
    company: Company,
    wedding: Wedding,
    service_tier: str | None = None,
    total_amount: Decimal | None = None,
    installments_count: int | None = None,
    signed_date: date | None = None,
    status: str | None = None,
) -> tuple[Contract, bool]:
    """Cria ou atualiza o contrato de honorários da assessoria para o casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: Instância do casamento associado.
        service_tier: Nível de serviço da assessoria cerimonial.
        total_amount: Valor total dos honorários.
        installments_count: Quantidade de parcelas acordada.
        signed_date: Data de assinatura do contrato.
        status: Status inicial ou atualizado do contrato.

    Returns:
        Tupla contendo a instância de Contract e um booleano indicando criação (True) ou atualização (False).

    Raises:
        BusinessRuleViolation: Se houver violação de validação nos dados contratuais.
    """
    created = False
    contract = (
        Contract.objects.for_tenant(company)
        .filter(
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
        )
        .first()
    )

    if not contract:
        tier = service_tier or Contract.ServiceTierChoices.COMPLETA
        contract = Contract(
            company=company,
            wedding=wedding,
            contract_type=Contract.ContractTypeChoices.PLANNER,
            service_tier=tier,
            name=f"Contrato de Assessoria ({tier})",
            total_amount=total_amount if total_amount is not None else Decimal("0.00"),
            installments_count=installments_count
            if installments_count is not None
            else 1,
            signed_date=signed_date,
            status=status or Contract.StatusChoices.DRAFT,
        )
        created = True
    else:
        if service_tier is not None:
            contract.service_tier = service_tier
            contract.name = f"Contrato de Assessoria ({service_tier})"
        if total_amount is not None:
            contract.total_amount = total_amount
        if installments_count is not None:
            contract.installments_count = installments_count
        if signed_date is not None:
            contract.signed_date = signed_date
        if status is not None:
            contract.status = status

    try:
        contract.save()
    except DjangoValidationError as exc:
        detail = (
            "; ".join(exc.messages)
            if hasattr(exc, "messages") and exc.messages
            else str(exc)
        )
        raise BusinessRuleViolation(
            detail=detail,
            code="planner_contract_validation_error",
        ) from exc

    return contract, created


def is_planner_contract_signed(
    *,
    company: Company,
    wedding: Wedding,
) -> bool:
    """Verifica se o contrato de assessoria cerimonial do casamento está formalmente assinado."""
    contract = get_planner_contract_for_wedding(company=company, wedding=wedding)
    return contract is not None and contract.status == Contract.StatusChoices.SIGNED


def sign_planner_contract_for_wedding(
    *,
    company: Company,
    wedding: Wedding,
    signed_date: date | None = None,
) -> Contract:
    """Assina formalmente o contrato de assessoria cerimonial do casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: Instância do casamento associado.
        signed_date: Data opcional da assinatura (se omitida, usa a data atual do contrato ou hoje).

    Returns:
        Instância de Contract assinada e salva.

    Raises:
        BusinessRuleViolation: Se o contrato não for encontrado ou violar regras de assinatura.
    """
    contract = get_planner_contract_for_wedding(company=company, wedding=wedding)
    if not contract:
        raise BusinessRuleViolation(
            detail="O casamento deve possuir um contrato de assessoria para iniciar o planejamento.",
            code="planner_contract_required",
        )

    contract.sign(signed_date or contract.signed_date)
    try:
        contract.save(update_fields=["status", "signed_date", "updated_at"])
    except DjangoValidationError as exc:
        detail = (
            "; ".join(exc.messages)
            if hasattr(exc, "messages") and exc.messages
            else str(exc)
        )
        raise BusinessRuleViolation(
            detail=detail,
            code="planner_contract_validation_error",
        ) from exc

    return contract


def enqueue_guest_count_evaluation(
    *,
    company_id: int | str,
    wedding_uuid: UUID | str,
    old_count: int,
    new_count: int,
) -> None:
    """Enfileira a avaliação de impacto da alteração de convidados pós-commit (RFC-001 / ADR-017)."""
    from django.db import transaction

    from apps.contracts.tasks import evaluate_guest_count_impact_task

    target_uuid = str(wedding_uuid)

    def _enqueue() -> None:
        evaluate_guest_count_impact_task.enqueue(
            company_id,
            target_uuid,
            old_count,
            new_count,
        )

    transaction.on_commit(_enqueue)


__all__ = [
    "enqueue_guest_count_evaluation",
    "get_contract_for_company",
    "get_planner_contract_for_wedding",
    "get_supplier_for_company",
    "is_planner_contract_signed",
    "list_contracts_for_wedding",
    "save_planner_contract_for_wedding",
    "sign_planner_contract_for_wedding",
]
