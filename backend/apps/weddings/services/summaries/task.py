import logging
from datetime import date

from django.db.models import F, Q

from apps.scheduler.models import Task
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskSummaryService:
    @staticmethod
    def urgent_tasks_count(*, company: Company, today: date | None = None) -> int:
        today = today or date.today()
        return (
            Task.objects.for_tenant(company)
            .filter(is_completed=False, due_date__lte=today)
            .count()
        )

    @staticmethod
    def wedding_task_stats(*, company: Company, wedding: Wedding) -> tuple[int, int]:
        tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
        total = tasks.count()
        completed = tasks.filter(is_completed=True).count()
        return completed, total

    @staticmethod
    def urgent_tasks(
        *, company: Company, wedding: Wedding, today: date | None = None, limit: int = 3
    ) -> list[dict]:
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
