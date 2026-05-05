import logging
from datetime import date

from django.core.management.base import BaseCommand

from apps.finances.models.installment import Installment


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Marca como OVERDUE todas as parcelas PENDING com due_date < hoje"

    def handle(self, *args, **kwargs):
        today = date.today()
        overdue_qs = Installment.objects.filter(
            status=Installment.StatusChoices.PENDING,
            due_date__lt=today,
        )

        count = overdue_qs.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS("Nenhuma parcela vencida encontrada."))
            return

        updated = overdue_qs.update(status=Installment.StatusChoices.OVERDUE)
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
