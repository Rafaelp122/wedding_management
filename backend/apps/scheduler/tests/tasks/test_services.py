from typing import Any, cast, no_type_check
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskPatchIn
from apps.scheduler.services.tasks import TaskService
from apps.scheduler.tests.factories import TaskFactory as _TaskFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def TaskFactory(*args: Any, **kwargs: Any) -> Task:
    return cast(Task, _TaskFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestTaskServiceCreate:
    """Testes de criação de tarefas via TaskService."""

    def test_create_task_success(self, user: Any) -> None:
        """Criação de tarefa vinculada ao casamento."""
        wedding = WeddingFactory(user_context=user)

        data: dict[str, Any] = {
            "wedding": wedding.uuid,
            "title": "Contratar Buffet",
            "description": "Fazer orçamento com 3 fornecedores",
        }

        task = TaskService.create(user.company, TaskIn(**data))

        assert task.wedding == wedding
        assert task.title == "Contratar Buffet"
        assert task.is_completed is False

    def test_create_task_with_wedding_instance(self, user: Any) -> None:
        """create() aceita UUID do Wedding."""
        wedding = WeddingFactory(user_context=user)

        data: dict[str, Any] = {
            "wedding": wedding.uuid,
            "title": "Enviar Convites",
        }

        task = TaskService.create(user.company, TaskIn(**data))
        assert task.wedding == wedding

    def test_create_task_wedding_not_found(self, user: Any) -> None:
        """UUID de wedding inexistente levanta ObjectNotFoundError."""
        data: dict[str, Any] = {
            "wedding": uuid4(),
            "title": "Tarefa Fantasma",
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            TaskService.create(user.company, TaskIn(**data))

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    def test_create_task_multitenancy(self) -> None:
        """Usuário A não pode criar tarefa com wedding do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)

        data: dict[str, Any] = {
            "wedding": wedding_b.uuid,
            "title": "Invasão",
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            TaskService.create(user_a.company, TaskIn(**data))

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    @no_type_check
    def test_create_task_rejects_wedding_instance_from_other_tenant(self) -> None:
        """Instância de Wedding pré-carregada também passa por validação tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        payload = TaskIn.model_construct(
            wedding=wedding_b,
            title="Invasão por instância",
            description="",
            due_date=None,
            is_completed=False,
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            TaskService.create(user_a.company, payload)

        assert exc_info.value.code == "wedding_not_found_or_denied"


@pytest.mark.django_db
class TestTaskServiceUpdate:
    """Testes de atualização de tarefas via TaskService."""

    def test_update_task_title(self, user: Any) -> None:
        """Atualização de título é permitida."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, title="Título Antigo")

        updated = TaskService.update(
            user.company, task, TaskPatchIn.model_construct(title="Título Novo")
        )

        assert updated.title == "Título Novo"

    def test_update_task_toggle_completed(self, user: Any) -> None:
        """Toggle de is_completed é permitido (ação principal do checklist)."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding, is_completed=False)

        updated = TaskService.update(
            user.company, task, TaskPatchIn.model_construct(is_completed=True)
        )

        assert updated.is_completed is True

    def test_update_task_cannot_change_wedding(self, user: Any) -> None:
        """Wedding é bloqueado no update."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding1)

        updated = TaskService.update(
            user.company, task, TaskPatchIn.model_construct(wedding=wedding2.uuid)
        )

        assert updated.wedding == wedding1

    def test_update_task_cross_tenant(self, user: Any) -> None:
        """Tarefa de outro tenant não pode ser atualizada."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        other_task = TaskFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            TaskService.update(
                user.company,
                other_task,
                TaskPatchIn.model_construct(title="Hack"),
            )


@pytest.mark.django_db
class TestTaskServiceDelete:
    """Testes de deleção de tarefas via TaskService."""

    def test_delete_task_success(self, user: Any) -> None:
        """Deleção de tarefa é permitida."""
        wedding = WeddingFactory(user_context=user)
        task = TaskFactory(wedding=wedding)

        TaskService.delete(user.company, instance=task)

        assert Task.objects.filter(uuid=task.uuid).count() == 0

    def test_delete_task_cross_tenant(self, user: Any) -> None:
        """Tarefa de outro tenant não pode ser deletada."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        other_task = TaskFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            TaskService.delete(user.company, instance=other_task)
