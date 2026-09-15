"""Comando para verificar prazos de tarefas do checklist e enviar notificações."""

import logging
from typing import Any

from django.core.management.base import BaseCommand

from apps.scheduler.services.tasks import TaskService


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Comando de verificação de prazos e atrasos em tarefas de checklist."""

    help = (
        "Verifica tarefas não concluídas com prazos vencidos ou próximos "
        "e dispara notificações assíncronas aos usuários da empresa."
    )

    def add_arguments(self, parser: Any) -> None:
        parser.add_argument(
            "--days-threshold",
            type=int,
            default=3,
            help="Janela em dias para alertar sobre tarefas a vencer (padrão: 3).",
        )
        parser.add_argument(
            "--company-id",
            type=int,
            default=None,
            help="ID opcional da empresa para restringir o escopo das notificações.",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        days_threshold = options.get("days_threshold", 3)
        company_id = options.get("company_id")
        company = None

        if company_id is not None:
            from apps.tenants.models import Company

            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f"Empresa com ID {company_id} não encontrada.")
                )
                return

        logger.info(
            "Iniciando verificação de prazos de tarefas (threshold=%d dias)...",
            days_threshold,
        )

        total_notified = TaskService.notify_due_tasks(
            company=company,
            days_threshold=days_threshold,
        )

        if total_notified == 0:
            self.stdout.write(
                self.style.SUCCESS("Nenhuma notificação de tarefa necessária.")
            )
            return

        self.stdout.write(
            self.style.SUCCESS(
                f"{total_notified} tarefa(s) geraram notificações com sucesso."
            )
        )
        logger.info(
            "Verificação de prazos concluída: %d tarefa(s) notificadas.",
            total_notified,
        )
