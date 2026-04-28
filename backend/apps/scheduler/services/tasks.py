import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.scheduler.models import Task
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskService:
    """
    Camada de serviço para gestão de tarefas (checklist).
    Purificada: Recebe instâncias resolvidas ou usa resolvers internos.
    """

    @staticmethod
    def list(
        user: AuthContextUser, wedding_id: UUID | str | None = None
    ) -> QuerySet[Task]:
        qs = Task.objects.for_user(user).select_related("wedding", "planner")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Task:
        planner = require_user(user)
        logger.info("Iniciando criação de Tarefa")

        wedding_input = data.pop("wedding")
        wedding = Wedding.objects.resolve(user, wedding_input)

        task = Task(planner=planner, wedding=wedding, **data)
        task.save()

        logger.info(f"Tarefa criada com sucesso: uuid={task.uuid}")
        return task

    @staticmethod
    @transaction.atomic
    def update(instance: Task, data: dict[str, Any]) -> Task:
        logger.info(f"Atualizando Tarefa uuid={instance.uuid}")

        data.pop("wedding", None)
        data.pop("planner", None)

        task_status = data.pop("is_completed", None)
        if task_status is not None:
            instance.is_completed = task_status

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Task) -> None:
        logger.info("Deletando Tarefa uuid=%s", instance.uuid)

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail="Não é possível apagar esta tarefa pois existem registros "
                "vinculados a ela.",
                code="task_protected_error",
            ) from e
