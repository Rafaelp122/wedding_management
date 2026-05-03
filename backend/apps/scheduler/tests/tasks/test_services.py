from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.scheduler.models import Task
from apps.scheduler.services.tasks import TaskService
from apps.scheduler.tests.factories import TaskFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestTaskServiceCreate:
    """Testes de criação de tarefas via TaskService."""

    def test_create_task_success(self, user):
        """Criação de tarefa vinculada ao casamento."""
        wedding = WeddingFactory(user_context=user)

        data = {
            "wedding": wedding.uuid,
            "title": "Contratar Buffet",
            "description": "Fazer orçamento com 3 fornecedores",
        }

        task = TaskService.create(user.company, data)

        assert task.wedding == wedding
        assert task.title == "Contratar Buffet"
        assert task.is_completed is False

    def test_create_task_with_wedding_instance(self, user):
        """create() aceita instância de Wedding."""
        wedding = WeddingFactory(user_context=user)

        data = {
            "wedding": wedding,
            "title": "Enviar Convites",
        }

        task = TaskService.create(user.company, data)
        assert task.wedding == wedding

    def test_create_task_wedding_not_found(self, user):
        """UUID de wedding inexistente levanta ObjectNotFoundError."""
        data = {
            "wedding": uuid4(),
            "title": "Tarefa Fantasma",
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            TaskService.create(user.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    def test_create_task_multitenancy(self):
        """Usuário A não pode criar tarefa com wedding do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)

        data = {
            "wedding": wedding_b.uuid,
            "title": "Invasão",
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            TaskService.create(user_a.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)


@pytest.mark.django_db
class TestTaskServiceUpdate:
    """Testes de atualização de tarefas via TaskService."""

    def test_update_task_title(self, user):
        """Atualização de título é permitida."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, title="Título Antigo")

        updated = TaskService.update(user.company, task, {"title": "Título Novo"})

        assert updated.title == "Título Novo"

    def test_update_task_toggle_completed(self, user):
        """Toggle de is_completed é permitido (ação principal do checklist)."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, is_completed=False)

        updated = TaskService.update(user.company, task, {"is_completed": True})

        assert updated.is_completed is True

    def test_update_task_cannot_change_wedding(self, user):
        """Wedding é bloqueado no update."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding1)

        updated = TaskService.update(user.company, task, {"wedding": wedding2.uuid})

        assert updated.wedding == wedding1

    def test_update_task_cannot_change_company(self, user):
        """Company é bloqueada no update."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding)
        other_user = UserFactory()

        updated = TaskService.update(
            user.company, task, {"company": other_user.company}
        )

        assert updated.company == user.company


@pytest.mark.django_db
class TestTaskServiceDelete:
    """Testes de deleção de tarefas via TaskService."""

    def test_delete_task_success(self, user):
        """Deleção de tarefa é permitida."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding)

        TaskService.delete(user.company, task.uuid)

        assert Task.objects.filter(uuid=task.uuid).count() == 0

    def test_delete_task_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            TaskService.delete(user.company, uuid4())


@pytest.mark.django_db
class TestTaskServiceListAndGet:
    """Testes de listagem e obtenção de tarefas."""

    def test_list_tasks_multitenancy(self):
        """list() retorna apenas tarefas do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        TaskFactory(wedding=wedding_a, title="Tarefa A")
        TaskFactory(wedding=wedding_b, title="Tarefa B")

        qs_a = TaskService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().title == "Tarefa A"

        qs_b = TaskService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().title == "Tarefa B"

    def test_list_tasks_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)

        TaskFactory(wedding=wedding1, title="Tarefa W1")
        TaskFactory(wedding=wedding2, title="Tarefa W2")

        qs = TaskService.list(user.company, wedding_id=wedding1.uuid)
        assert qs.count() == 1
        assert qs.first().title == "Tarefa W1"

    def test_get_task_success(self, user):
        """get() retorna tarefa por UUID."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, title="Confirmar Convidados")

        result = TaskService.get(user.company, task.uuid)
        assert result.uuid == task.uuid
        assert result.title == "Confirmar Convidados"

    def test_get_task_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            TaskService.get(user.company, uuid4())

    def test_get_task_multitenancy(self):
        """Usuário A não pode acessar tarefa do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        task_b = TaskFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            TaskService.get(user_a.company, task_b.uuid)
