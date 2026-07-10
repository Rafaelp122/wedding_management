import logging
from datetime import date
from typing import Any

from django.db.models import F, Q

from apps.scheduler.models import Task
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskSummaryService:
    """
    Camada de serviço para consolidação de resumos e estatísticas de tarefas.
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
        return (
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
        total = tasks.count()
        completed = tasks.filter(is_completed=True).count()
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
