import logging

from django.db import transaction

from apps.core.shortcuts import resolve_tenant_resource
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
    @transaction.atomic
    def create(company: Company, payload: TaskIn) -> Task:
        """
        Cria uma nova tarefa para o tenant especificado.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação da tarefa.

        Returns:
            A tarefa criada e salva no banco de dados.

        Raises:
            ObjectNotFoundError: Se o casamento associado não for encontrado ou
                pertencer a outro tenant.
        """
        logger.info(f"Iniciando criação de Tarefa para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)
        wedding_input = data.pop("wedding", None)

        wedding = resolve_tenant_resource(
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
        """
        Atualiza as informações de uma tarefa existente.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da tarefa a ser atualizada.
            payload: Dados com as alterações a serem aplicadas.

        Returns:
            A instância da tarefa atualizada.

        Raises:
            ObjectNotFoundError: Se a tarefa pertencer a outro tenant.
        """
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
        """
        Exclui uma tarefa existente.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da tarefa a ser excluída.

        Raises:
            ObjectNotFoundError: Se a tarefa pertencer a outro tenant.
        """
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
            f"Tarefa uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
        )
