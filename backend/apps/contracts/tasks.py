"""Tarefas assíncronas do domínio de Contratos e Termos Aditivos.

Utiliza a infraestrutura de background jobs nativa django.tasks (ADR-017).
"""

from __future__ import annotations

import logging
from decimal import Decimal

from django.tasks import task


logger = logging.getLogger(__name__)


@task()
def on_contract_addendum_signed_task(
    company_id: int | str,
    contract_id: str,
    addendum_id: str,
    amount: str | Decimal,
) -> None:
    """Reação pós-commit à assinatura de termo aditivo (RFC-001 / ADR-017).

    Valida a cadeia company → contrato → aditivo via interfaces internas e
    registra o evento para consumo futuro (notifications/dashboard, Onda 4).
    Sem efeitos colaterais: o ajuste financeiro já ocorreu de forma síncrona
    em `ContractAddendumService.sign`.

    Args:
        company_id: ID numérico ou UUID da empresa tenant.
        contract_id: Identificador ou UUID do contrato principal.
        addendum_id: Identificador ou UUID do aditivo assinado.
        amount: Montante do aditivo (string serializável ou Decimal).
    """
    from apps.contracts.interfaces import get_contract_for_company
    from apps.contracts.models import ContractAddendum
    from apps.core.exceptions import ObjectNotFoundError
    from apps.tenants.models import Company

    company = (
        Company.objects.get(pk=company_id)
        if isinstance(company_id, int)
        else Company.objects.get(uuid=company_id)
    )
    try:
        contract = get_contract_for_company(
            company=company, contract_uuid_or_id=contract_id
        )
    except ObjectNotFoundError:
        logger.warning(
            "Aditivo assinado ignorado: contrato %s não encontrado para empresa %s.",
            contract_id,
            company.id,
        )
        return

    addendum = (
        ContractAddendum.objects.for_tenant(company)
        .filter(uuid=addendum_id, contract_id=contract.id)
        .first()
    )
    if addendum is None:
        logger.warning(
            "Aditivo assinado ignorado: aditivo %s não pertence ao contrato %s.",
            addendum_id,
            contract.uuid,
        )
        return

    logger.info(
        "Aditivo assinado pós-commit: company=%s contract=%s addendum=%s amount=%s status=%s",
        company.id,
        contract.uuid,
        addendum.uuid,
        Decimal(str(amount)),
        addendum.status,
    )

    from apps.notifications.interfaces import notify_contract_addendum_signed

    wedding = contract.wedding
    wedding_name = None
    if wedding is not None:
        bride = getattr(wedding, "bride_name", "") or ""
        groom = getattr(wedding, "groom_name", "") or ""
        wedding_name = f"{groom} & {bride}".strip(" &") or None

    users = [u for u in company.users.all() if u.is_active]
    notify_contract_addendum_signed(
        company=company,
        contract_name=contract.name or str(contract.uuid),
        addendum_amount=Decimal(str(amount)),
        addendum_uuid=addendum.uuid,
        wedding_uuid=wedding.uuid if wedding is not None else None,
        wedding_name=wedding_name,
        users=users,
    )


@task()
def evaluate_guest_count_impact_task(
    company_id: int | str,
    wedding_uuid: str,
    old_count: int,
    new_count: int,
) -> None:
    """
    Avalia o impacto da alteração no número de convidados sobre contratos
    (RFC-001 / ADR-017). Consumidor assíncrono disparado via enqueue_guest_count_evaluation.
    Identifica fornecedores sensíveis ao headcount (buffet, bebidas,
    mobiliário, doces) e registra orientações para conferência do cerimonial.
    """
    from apps.contracts.interfaces import list_contracts_for_wedding
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding

    company = (
        Company.objects.get(pk=company_id)
        if isinstance(company_id, int)
        else Company.objects.get(uuid=company_id)
    )

    wedding = Wedding.objects.for_tenant(company).filter(uuid=wedding_uuid).first()
    if not wedding:
        logger.warning(
            "Casamento %s não encontrado para empresa %s na avaliação de convidados.",
            wedding_uuid,
            company.id,
        )
        return

    diff = new_count - old_count
    logger.info(
        "Avaliando impacto de convidados no casamento %s: %d -> %d (diferença: %+d)",
        wedding.uuid,
        old_count,
        new_count,
        diff,
    )

    keywords = [
        "buffet",
        "bebida",
        "bar",
        "doce",
        "bolo",
        "mesa",
        "cadeira",
        "mobiliario",
    ]
    contracts = list_contracts_for_wedding(company=company, wedding_uuid=wedding.uuid)
    impacted_contracts = []
    for c in contracts:
        name_lower = c.name.lower()
        if any(kw in name_lower for kw in keywords):
            impacted_contracts.append(c.name)

    if impacted_contracts:
        logger.warning(
            "Contratos potencialmente impactados pela alteração de convidados no casamento %s: %s",
            wedding.uuid,
            ", ".join(impacted_contracts),
        )
