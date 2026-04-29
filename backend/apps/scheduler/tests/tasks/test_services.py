import pytest

from apps.events.tests.factories import EventFactory
from apps.scheduler.models.task import Task
from apps.scheduler.services.tasks import TaskService
from apps.scheduler.tests.appointment_factories import TaskFactory


@pytest.mark.django_db
@pytest.mark.service
class TestTaskService:
    """Testes de lógica de negócio para o TaskService."""

    def test_create_task_success(self, user):
        """Domínio: Criação de tarefa vinculada ao casamento."""
        event = EventFactory(company=user.company)
        data = {
            "event": event.uuid,
            "title": "Escolher Vestido",
            "due_date": "2026-06-01",
        }

        task = TaskService.create(user=user, data=data)
        assert task.event == event
        assert task.company == user.company
        assert task.is_completed is False

    def test_update_task_completion(self, user):
        """Domínio: Marcação de tarefa como concluída."""
        task = TaskFactory(event__company=user.company, is_completed=False)

        updated_task = TaskService.update(instance=task, data={"is_completed": True})
        assert updated_task.is_completed is True

    def test_delete_task_success(self, user):
        """Domínio: Deleção física da tarefa."""
        task = TaskFactory(event__company=user.company)
        TaskService.delete(instance=task)
        assert Task.objects.filter(uuid=task.uuid).count() == 0
