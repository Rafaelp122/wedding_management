import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import DomainIntegrityError, ObjectNotFoundError
from apps.core.types import AuthContextUser
from apps.scheduler.models import Task
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskService:
    """
    Camada de serviço para gestão de tarefas (checklist).
    Garante isolamento total (Multitenancy), validações e integridade.
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
    def get(user: AuthContextUser, uuid: UUID | str) -> Task:
        task = (
            Task.objects.for_user(user)
            .select_related("wedding", "planner")
            .filter(uuid=uuid)
            .first()
        )
        if task is None:
            raise ObjectNotFoundError(
                detail="Tarefa não encontrada ou acesso negado.",
                code="task_not_found_or_denied",
            )
        return task

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Task:
        planner = require_user(user)
        logger.info(f"Iniciando criação de Tarefa para planner_id={planner.id}")

        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.for_user(planner).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de criar tarefa em casamento inválido ou "
                    f"negado: {wedding_input} por planner_id={planner.id}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou você não tem permissão para "
                    "acessá-lo.",
                    code="wedding_not_found_or_denied",
                ) from e

        task = Task(planner=planner, wedding=wedding, **data)
        task.save()

        logger.info(
            f"Tarefa criada com sucesso: uuid={task.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return task

    @staticmethod
    @transaction.atomic
    def update(user: AuthContextUser, instance: Task, data: dict[str, Any]) -> Task:
        planner = require_user(user)
        logger.info(
            f"Atualizando Tarefa uuid={instance.uuid} por planner_id={planner.id}"
        )

        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Tarefa uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, uuid: UUID | str, data: dict[str, Any]
    ) -> Task:
        instance = TaskService.get(user, uuid)
        return TaskService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, uuid: UUID | str) -> None:
        instance = TaskService.get(user, uuid)
        planner = require_user(user)
        logger.info(
            f"Tentativa de deleção da Tarefa uuid={instance.uuid} por "
            f"planner_id={planner.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Tarefa uuid={instance.uuid} DESTRUÍDA por planner_id={planner.id}"
            )
        except ProtectedError as e:
            logger.error(f"Falha de integridade ao deletar tarefa uuid={instance.uuid}")
            raise DomainIntegrityError(
                detail="Não é possível apagar esta tarefa pois existem registros "
                "vinculados a ela.",
                code="task_protected_error",
            ) from e
