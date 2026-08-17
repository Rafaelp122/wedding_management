"""
Selectors para o domínio de Tarefas (Checklist).
Consultas otimizadas e encapsuladas de leitura para Task.
"""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
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
        select_related=["wedding"],
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
