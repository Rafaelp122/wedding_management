"""
Tarefas assíncronas do domínio de casamentos (Weddings).
Utiliza a infraestrutura de background jobs nativa django.tasks (ADR-017).
"""

from __future__ import annotations

import logging

from django.tasks import task


logger = logging.getLogger(__name__)


@task()
def on_wedding_canceled_task(company_id: int | str, wedding_uuid: str) -> None:
    """
    Tarefa assíncrona coordenadora executada após o cancelamento de um casamento.
    Orquestra os efeitos colaterais nos outros domínios de forma assíncrona
    e desacoplada:
    - Limpeza/desativação de eventos de agenda (scheduler)
    - Despacho de notificações de cancelamento

    Args:
        company_id: ID numérico ou UUID da empresa tenant.
        wedding_uuid: Identificador UUID do casamento cancelado.
    """
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
            "Casamento %s não encontrado para empresa %s na task de cancelamento.",
            wedding_uuid,
            company.id,
        )
        return

    logger.info(
        "Executando task de cancelamento pós-commit para casamento %s na empresa %s.",
        wedding.uuid,
        company.id,
    )


@task()
def on_wedding_activated_task(
    company_id: int | str,
    wedding_uuid: str,
    template: str | None = None,
) -> None:
    """
    Tarefa assíncrona executada após a ativação de um casamento (PROPOSTA -> IN_PROGRESS).
    Orquestra a geração assíncrona de itens operacionais e notificações reativas.

    Args:
        company_id: ID numérico ou UUID da empresa tenant.
        wedding_uuid: Identificador UUID do casamento ativado.
        template: Nome do template de cronograma, se houver.
    """
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
            "Casamento %s não encontrado para empresa %s na task de ativação.",
            wedding_uuid,
            company.id,
        )
        return

    logger.info(
        "Executando task de ativação pós-commit para casamento %s na empresa %s (template=%s).",
        wedding.uuid,
        company.id,
        template,
    )

    # Dispara a geração assíncrona do checklist operacional inicial (RFC-001 / ADR-017)
    from apps.scheduler.interfaces import enqueue_wedding_checklist_generation

    enqueue_wedding_checklist_generation(
        company_id=company.id,
        wedding_uuid=str(wedding.uuid),
        template=template,
    )
