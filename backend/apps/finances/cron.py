import logging

from django.core.management import call_command

from apps.core.cron import cron_registry


logger = logging.getLogger(__name__)


@cron_registry.register(
    "mark_overdue_installments",
    description="Marca parcelas pendentes com vencimento anterior a hoje como OVERDUE.",
)
def run_mark_overdue_installments() -> str:
    """Executa a verificação e atualização de parcelas vencidas."""
    call_command("mark_overdue_installments")
    return "Parcelas vencidas verificadas e atualizadas com sucesso."
