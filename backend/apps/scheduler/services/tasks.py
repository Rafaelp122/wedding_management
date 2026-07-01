import logging
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskService:
    """
    Camada de serviço para gestão de tarefas (checklist).
    Garante isolamento total (Multitenancy), lógicas de negócio e integridade.
    """

    @staticmethod
    def list(company: Company, wedding_id: UUID | str | None = None) -> QuerySet[Task]:
        qs = Task.objects.for_tenant(company).select_related("wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Task:
        return get_object_or_404_for_tenant(
            Task,
            company,
            uuid,
            select_related=["wedding"],
            code="task_not_found_or_denied",
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: TaskIn) -> Task:
        logger.info(f"Iniciando criação de Tarefa para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            wedding = get_object_or_404_for_tenant(
                Wedding,
                company,
                wedding_input,
                code="wedding_not_found_or_denied",
                detail="Acesso negado ao casamento.",
            )

        task = Task(company=company, wedding=wedding, **data)
        task.save()

        logger.info(
            f"Tarefa criada com sucesso: uuid={task.uuid} no casamento "
            f"uuid={wedding.uuid}"
        )
        return task

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Task, payload: TaskPatchIn) -> Task:
        validate_tenant_ownership(
            company,
            instance,
            detail="Tarefa não encontrada ou acesso negado.",
            code="task_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Tarefa uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Tarefa uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Task) -> None:
        validate_tenant_ownership(
            company,
            instance,
            detail="Tarefa não encontrada ou acesso negado.",
            code="task_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção da Tarefa uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        instance.delete()
        logger.warning(
            f"Tarefa uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
        )
