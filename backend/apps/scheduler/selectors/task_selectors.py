"""
Selectors para o domínio de Tarefas (Checklist).
Consultas otimizadas e encapsuladas de leitura para Task.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Any
from uuid import UUID

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.scheduler.managers import TaskQuerySet
from apps.scheduler.models import Task


if TYPE_CHECKING:
    from apps.tenants.models import Company


def task_list_selector(
    *,
    company: Company,
    wedding_id: UUID | str | None = None,
    is_completed: bool | None = None,
) -> TaskQuerySet:
    """
    Lista tarefas do checklist vinculadas ao tenant, com filtros opcionais.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_id: Identificador opcional do casamento para filtragem.
        is_completed: Flag booleana opcional para filtrar por status de conclusão.

    Returns:
        TaskQuerySet com as tarefas filtradas e relacionamento com wedding carregado.
    """
    qs = Task.objects.for_tenant(company).select_related("wedding")
    if wedding_id:
        qs = qs.for_wedding(wedding_id)
    if is_completed is not None:
        qs = qs.completed() if is_completed else qs.pending()
    return qs


def task_get_selector(*, company: Company, uuid: UUID | str) -> Task:
    """
    Recupera uma tarefa específica pelo UUID, garantindo o isolamento multitenant.

    Args:
        company: O tenant atual para isolamento de dados.
        uuid: O identificador único da tarefa.

    Returns:
        A instância da Task encontrada.

    Raises:
        ObjectNotFoundError: Se a tarefa não existir ou pertencer a outro tenant.
    """
    return get_object_or_404_for_tenant(
        Task,
        company,
        uuid,
        select_related=["wedding", "company"],
        code="task_not_found_or_denied",
    )


def task_urgent_list_selector(*, company: Company, today: date) -> TaskQuerySet:
    """
    Lista tarefas urgentes (pendentes e vencidas/a vencer até hoje) do tenant.

    Args:
        company: O tenant atual para isolamento de dados.
        today: Data de referência para verificar urgência/vencimento.

    Returns:
        TaskQuerySet com as tarefas urgentes.
    """
    return Task.objects.for_tenant(company).select_related("wedding").urgent(today)


def get_wedding_timeline_compression_selector(
    *,
    company: Company,
    wedding_uuid: UUID | str,
) -> dict[str, Any]:
    """
    Analisa a linha do tempo do casamento para detectar compressão temporal (RFC-001).

    Calcula a proximidade da celebração (se inferior a 90 dias) e gera alertas orientadores
    para a assessoria priorizar etapas críticas.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding_uuid: UUID do casamento a analisar.

    Returns:
        Dicionário com is_timeline_compressed, compressed_timeline_message e days_until_wedding.
    """
    from django.utils import timezone

    from apps.weddings.models import Wedding

    wedding = get_object_or_404_for_tenant(
        Wedding,
        company,
        wedding_uuid,
        code="wedding_not_found_or_denied",
    )

    today = timezone.localdate()
    if not wedding.date:
        return {
            "is_timeline_compressed": False,
            "compressed_timeline_message": None,
            "days_until_wedding": None,
        }

    days_until_wedding = (wedding.date - today).days
    is_compressed = days_until_wedding < 90
    message: str | None = None

    if is_compressed:
        if days_until_wedding < 0:
            message = (
                "Celebração realizada. Verifique pendências e encerramento operacional."
            )
        elif days_until_wedding <= 30:
            message = (
                f"Atenção crítica: Restam apenas {days_until_wedding} dias até a celebração! "
                "Cronograma em reta final urgente."
            )
        else:
            message = (
                f"Atenção: Cronograma comprimido ({days_until_wedding} dias até a celebração). "
                "Recomenda-se priorizar a contratação de itens essenciais e checklist crítico."
            )

    return {
        "is_timeline_compressed": is_compressed,
        "compressed_timeline_message": message,
        "days_until_wedding": days_until_wedding,
    }
