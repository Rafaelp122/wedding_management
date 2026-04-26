import pytest

from apps.scheduler.models.task import Task
from apps.scheduler.services.tasks import TaskService
from apps.scheduler.tests.factories import TaskFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestTaskService:
    """Testes de lógica de negócio para o TaskService."""

    def test_create_task_success(self, user):
        """Domínio: Criação de tarefa vinculada ao casamento."""
        wedding = WeddingFactory(planner=user)
        data = {
            "wedding": wedding.uuid,
            "title": "Escolher Vestido",
            "due_date": "2026-06-01",
        }

        task = TaskService.create(user=user, data=data)
        assert task.wedding == wedding
        assert task.planner == user
        assert task.is_completed is False

    def test_update_task_completion(self, user):
        """Domínio: Marcação de tarefa como concluída."""
        task = TaskFactory(wedding__planner=user, is_completed=False)

        updated_task = TaskService.update(instance=task, data={"is_completed": True})
        assert updated_task.is_completed is True

    def test_delete_task_success(self, user):
        """Domínio: Deleção física da tarefa."""
        task = TaskFactory(wedding__planner=user)
        TaskService.delete(instance=task)
        assert Task.objects.filter(uuid=task.uuid).count() == 0
