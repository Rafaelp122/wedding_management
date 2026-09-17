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
