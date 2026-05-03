from datetime import date, timedelta

import pytest

from apps.scheduler.models import Task
from apps.scheduler.tests.factories import TaskFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestTaskModelMetadata:
    """Testes de representação e metadados do modelo Task."""

    def test_task_str_shows_checkbox_and_title(self, user):
        """__str__ deve conter [ ] ou [x] e o título."""
        wedding = WeddingFactory(user_context=user)
        task_pending = Task(
            company=user.company,
            wedding=wedding,
            title="Contratar Buffet",
            is_completed=False,
        )
        assert str(task_pending) == "[ ] Contratar Buffet"

        task_done = Task(
            company=user.company,
            wedding=wedding,
            title="Enviar Convites",
            is_completed=True,
        )
        assert str(task_done) == "[x] Enviar Convites"

    def test_task_ordering_pending_first(self, user):
        """Ordenação: is_completed (False primeiro), due_date, created_at."""
        wedding = WeddingFactory(user_context=user)
        today = date.today()

        t_completed = TaskFactory(wedding=wedding, is_completed=True, title="Feito")
        t_pending_late = TaskFactory(
            wedding=wedding,
            is_completed=False,
            title="Pendente Tarde",
            due_date=today + timedelta(days=30),
        )
        t_pending_soon = TaskFactory(
            wedding=wedding,
            is_completed=False,
            title="Pendente Urgente",
            due_date=today + timedelta(days=5),
        )

        tasks = list(Task.objects.all())
        # Pendentes primeiro, ordenados por due_date
        assert tasks[0] == t_pending_soon
        assert tasks[1] == t_pending_late
        assert tasks[2] == t_completed

    def test_task_is_completed_default_false(self, user):
        """is_completed padrão deve ser False."""
        wedding = WeddingFactory(user_context=user)
        task = Task(company=user.company, wedding=wedding, title="Teste")
        assert task.is_completed is False

    def test_task_due_date_nullable(self, user):
        """due_date pode ser nulo (tarefa sem prazo)."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, due_date=None)
        task.full_clean()
