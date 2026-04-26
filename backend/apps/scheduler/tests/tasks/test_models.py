import pytest

from apps.scheduler.models.task import Task
from apps.scheduler.tests.factories import TaskFactory


@pytest.mark.django_db
@pytest.mark.unit
class TestTaskModel:
    """Testes de integridade física do modelo Task."""

    def test_task_str(self):
        task = Task(title="Comprar Flores", is_completed=False)
        assert str(task) == "[ ] Comprar Flores"

        task.is_completed = True
        assert str(task) == "[x] Comprar Flores"

    def test_task_ordering(self):
        """Garante que tarefas pendentes vêm antes das concluídas."""
        t1 = TaskFactory(title="Pendente", is_completed=False)
        t2 = TaskFactory(title="Concluída", is_completed=True)

        qs = Task.objects.filter(id__in=[t1.id, t2.id])
        # Ordering: ["is_completed", "due_date"] -> False vem antes de True
        assert list(qs) == [t1, t2]
