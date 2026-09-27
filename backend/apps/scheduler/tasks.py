"""
Tarefas assíncronas do domínio de Agendamento e Checklist (Scheduler).
Utiliza a infraestrutura de background jobs nativa django.tasks (ADR-017 / ADR-031).
"""

from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from django.tasks import task
from django.utils import timezone


logger = logging.getLogger(__name__)


DEFAULT_CHECKLIST_TEMPLATES: list[dict[str, Any]] = [
    {
        "title": "Definir local da cerimônia e recepção",
        "description": "Visitar espaços, checar alvarás, infraestrutura e capacidade de convidados.",
        "priority": "HIGH",
        "offset_days": 300,
    },
    {
        "title": "Contratar serviço de buffet e bebidas",
        "description": "Definir cardápio, realizar degustação e fechar contrato de alimentação.",
        "priority": "HIGH",
        "offset_days": 240,
    },
    {
        "title": "Contratar equipe de fotografia e vídeo",
        "description": "Selecionar fotógrafos e cinegrafistas com o estilo visual desejado pelo casal.",
        "priority": "HIGH",
        "offset_days": 210,
    },
    {
        "title": "Escolher decoração, flores e iluminação",
        "description": "Desenvolver projeto cenográfico e aprovar plantas de layout.",
        "priority": "MEDIUM",
        "offset_days": 180,
    },
    {
        "title": "Degustação de doces, bolo e sobremesas",
        "description": "Aprovar doces finos, sabores de bolo e mesa de café.",
        "priority": "MEDIUM",
        "offset_days": 120,
    },
    {
        "title": "Escolher e enviar convites aos convidados",
        "description": "Enviar Save the Date prévio e convites com link de confirmação RSVP.",
        "priority": "MEDIUM",
        "offset_days": 90,
    },
    {
        "title": "Provas finais de cabelo, maquiagem e trajes",
        "description": "Realizar teste de maquiagem, penteado e ajustes finais no vestido e terno.",
        "priority": "MEDIUM",
        "offset_days": 30,
    },
    {
        "title": "Elaborar roteiro minucioso do grande dia",
        "description": "Mapear minuto a minuto os horários de montagem, cerimônia e recepção.",
        "priority": "URGENT",
        "offset_days": 15,
    },
    {
        "title": "Reunião de alinhamento final com todos os fornecedores",
        "description": "Confirmar horários de montagem, entregas de materiais e contatos de emergência.",
        "priority": "URGENT",
        "offset_days": 7,
    },
]


@task()
def generate_checklist_from_template_task(
    company_id: int | str,
    wedding_uuid: str,
    template: str | None = None,
) -> None:
    """
    Gera automaticamente o checklist operacional inicial para um casamento ativado (RFC-001 / RF-18).
    Executado de forma assíncrona desacoplada via django.tasks.

    Args:
        company_id: ID numérico ou UUID da empresa tenant.
        wedding_uuid: UUID do casamento.
        template: Nome do template de cronograma, se houver.
    """
    from apps.scheduler.models import ChecklistItem
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
            "Casamento %s não encontrado para empresa %s na geração de checklist.",
            wedding_uuid,
            company.id,
        )
        return

    # Se já existirem itens de checklist, evita duplicidade
    if ChecklistItem.objects.for_tenant(company).for_wedding(wedding).exists():
        logger.info(
            "Casamento %s já possui itens de checklist cadastrados. Pulando geração.",
            wedding.uuid,
        )
        return

    wedding_date = wedding.date
    today = timezone.localdate()

    items_to_create = []
    for item_data in DEFAULT_CHECKLIST_TEMPLATES:
        due_date = None
        if wedding_date:
            offset: int = int(item_data["offset_days"])
            due_date = wedding_date - timedelta(days=offset)
            if due_date < today:
                due_date = today + timedelta(days=7)

        items_to_create.append(
            ChecklistItem(
                company=company,
                wedding=wedding,
                title=str(item_data["title"]),
                description=str(item_data["description"]),
                priority=str(item_data["priority"]),
                due_date=due_date,
                is_completed=False,
            )
        )

    ChecklistItem.objects.bulk_create(items_to_create)
    logger.info(
        "Checklist gerado com sucesso: %d itens criados para o casamento %s (empresa %s).",
        len(items_to_create),
        wedding.uuid,
        company.id,
    )
