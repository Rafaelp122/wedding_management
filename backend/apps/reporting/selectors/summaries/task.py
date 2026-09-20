"""
Selectors para consolidação de resumos e estatísticas de tarefas.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING, Any

from django.db.models import Count, F, Q

from apps.scheduler.models import Task


if TYPE_CHECKING:
    from apps.tenants.models import Company
    from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskSummarySelector:
    """
    Camada de consulta para consolidação de resumos e estatísticas de tarefas.
    Agrega informações sobre tarefas atrasadas, totais por casamento
    e listagens de pendências urgentes do tenant.
    """

    @staticmethod
    def urgent_tasks_count(*, company: Company, today: date | None = None) -> int:
        """
        Retorna a quantidade de tarefas não concluídas e atrasadas do tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência (caso não informada, usa a data atual).

        Returns:
            Quantidade total de tarefas atrasadas.
        """
        today = today or date.today()
        return int(
            Task.objects.for_tenant(company)
            .filter(is_completed=False, due_date__lte=today)
            .count()
        )

    @staticmethod
    def wedding_task_stats(*, company: Company, wedding: Wedding) -> tuple[int, int]:
        """
        Retorna as estatísticas de tarefas concluídas e totais de um casamento.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento a ser consultado.

        Returns:
            Uma tupla contendo (tarefas_concluidas, total_tarefas).
        """
        tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
        total = int(tasks.count())
        completed = int(tasks.filter(is_completed=True).count())
        return completed, total

    @staticmethod
    def urgent_tasks(
        *, company: Company, wedding: Wedding, today: date | None = None, limit: int = 3
    ) -> list[dict[str, Any]]:
        """
        Retorna as tarefas urgentes (atrasadas ou sem prazo) de um casamento.

        Ordena as tarefas de forma ascendente pela data de vencimento, com
        valores nulos ao final.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding: Instância do casamento a ser consultado.
            today: Data de referência (caso não informada, usa a data atual).
            limit: Limite máximo de tarefas a serem retornadas (padrão: 3).

        Returns:
            Lista contendo até `limit` dicionários com as chaves `uuid`, `title`
            e `due_date`.
        """
        today = today or date.today()
        urgent = (
            Task.objects.for_tenant(company)
            .filter(wedding=wedding, is_completed=False)
            .filter(Q(due_date__lte=today) | Q(due_date__isnull=True))
            .order_by(F("due_date").asc(nulls_last=True))[:limit]
        )
        return [
            {
                "uuid": t.uuid,
                "title": t.title,
                "due_date": t.due_date,
            }
            for t in urgent
        ]

    @staticmethod
    def tasks_progress_by_wedding(
        company: Company, year: int | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Agrupa tarefas por casamento no tenant via SQL Count("id") e
        Count("id", filter=Q(is_completed=True)).

        Args:
            company: O tenant atual para isolamento de dados.
            year: Ano opcional para filtragem dos casamentos (wedding__date__year=year).
            limit: Quantidade máxima de casamentos retornados (padrão: 10).

        Returns:
            Lista ordenada pelo volume total de tarefas em ordem decrescente,
            contendo wedding_uuid, wedding_name, total_tasks, completed_tasks
            e progress_pct.
        """
        qs = Task.objects.for_tenant(company)
        if year is not None:
            qs = qs.filter(wedding__date__year=year)

        grouped = (
            qs.values(
                "wedding__uuid",
                "wedding__bride_name",
                "wedding__groom_name",
            )
            .annotate(
                total_tasks=Count("id"),
                completed_tasks=Count("id", filter=Q(is_completed=True)),
            )
            .order_by("-total_tasks", "wedding__bride_name")[:limit]
        )

        result: list[dict[str, Any]] = []
        for row in grouped:
            total = int(row["total_tasks"])
            completed = int(row["completed_tasks"])
            progress_pct = round((completed / total) * 100) if total > 0 else 0
            bride = row["wedding__bride_name"] or ""
            groom = row["wedding__groom_name"] or ""
            wedding_name = f"{bride} e {groom}".strip()
            result.append(
                {
                    "wedding_uuid": row["wedding__uuid"],
                    "wedding_name": wedding_name,
                    "total_tasks": total,
                    "completed_tasks": completed,
                    "progress_pct": progress_pct,
                }
            )
        return result

    @staticmethod
    def urgent_tasks_detail(
        *,
        company: Company,
        today: date | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """
        Retorna as Top N tarefas atrasadas do tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            today: Data de referência (caso não informada, usa a data atual).
            limit: Quantidade máxima de registros retornados (padrão: 10).

        Returns:
            Lista de dicionários contendo uuid, wedding_name, title e due_date.
        """
        today = today or date.today()

        tasks = (
            Task.objects.for_tenant(company)
            .filter(is_completed=False, due_date__lte=today)
            .select_related("wedding")
            .order_by("due_date", "created_at")[:limit]
        )

        return [
            {
                "uuid": t.uuid,
                "wedding_name": (
                    f"{t.wedding.bride_name} e {t.wedding.groom_name}"
                    if t.wedding
                    else ""
                ),
                "title": t.title,
                "due_date": t.due_date,
            }
            for t in tasks
        ]


tasks_progress_by_wedding = TaskSummarySelector.tasks_progress_by_wedding
urgent_tasks_detail = TaskSummarySelector.urgent_tasks_detail
