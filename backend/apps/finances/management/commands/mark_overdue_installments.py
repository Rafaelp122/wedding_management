import logging
from datetime import date

from django.core.management.base import BaseCommand

from apps.finances.services.installment_service import InstallmentService


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Marca como OVERDUE todas as parcelas PENDING com due_date < hoje"

    def handle(self, *args, **kwargs):
        today = date.today()
        updated = InstallmentService.mark_overdue_installments(today=today)

        if updated == 0:
            self.stdout.write(self.style.SUCCESS("Nenhuma parcela vencida encontrada."))
            return

        self.stdout.write(
            self.style.WARNING(
                f"{updated} parcela(s) marcada(s) como OVERDUE "
                f"(vencidas antes de {today})."
            )
        )
        logger.info(
            "mark_overdue_installments: %d parcela(s) marcada(s) como OVERDUE.",
            updated,
        )
