import logging
from datetime import date, timedelta

from django.db import transaction
from django.utils import timezone

from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.notifications.interfaces import send_notification_async
from apps.scheduler.models import Task
from apps.scheduler.schemas import TaskIn, TaskPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class TaskService:
    """
    Camada de serviço para gestão de tarefas (checklist).
    Garante isolamento total (Multitenancy), lógicas de negócio e integridade.

    Regras de Negócio e SSOT:
    - Hub do Domínio do Cronograma:
      docs/architecture/domains/scheduler-domain.md
    - Notificações de Vencimento de Tarefas:
      docs/architecture/business-rules/notifications/in-app-notifications-rules.md
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
        data.pop("wedding", None)
        data.pop("company", None)

        updated_fields: set[str] = set()

        if "is_completed" in data:
            is_completed = data.pop("is_completed")
            if is_completed is True:
                instance.complete()
            elif is_completed is False:
                instance.reopen()
            updated_fields.add("is_completed")

        details_kwargs = {}
        for field in ("title", "description", "due_date"):
            if field in data:
                details_kwargs[field] = data.pop(field)
                updated_fields.add(field)

        if details_kwargs:
            instance.update_details(**details_kwargs)

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            instance.save(update_fields=list(updated_fields))

        logger.info(f"Tarefa uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def complete(company: Company, instance: Task) -> Task:
        """Marca a tarefa como concluída no contexto do tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A tarefa a ser concluída.

        Returns:
            Task: A tarefa atualizada.

        Raises:
            ObjectNotFoundError: Se a tarefa pertencer a outro tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Tarefa não encontrada ou acesso negado.",
            code="task_not_found_or_denied",
        )
        instance.complete()
        instance.save(update_fields=["is_completed", "updated_at"])
        logger.info(f"Tarefa uuid={instance.uuid} concluída com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def reopen(company: Company, instance: Task) -> Task:
        """Reabre uma tarefa concluída no contexto do tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A tarefa a ser reaberta.

        Returns:
            Task: A tarefa atualizada.

        Raises:
            ObjectNotFoundError: Se a tarefa pertencer a outro tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Tarefa não encontrada ou acesso negado.",
            code="task_not_found_or_denied",
        )
        instance.reopen()
        instance.save(update_fields=["is_completed", "updated_at"])
        logger.info(f"Tarefa uuid={instance.uuid} reaberta com sucesso.")
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

    @staticmethod
    def notify_due_tasks(
        company: Company | None = None,
        days_threshold: int = 3,
        today: date | None = None,
    ) -> int:
        """Notifica usuários ativos sobre tarefas atrasadas ou próximas do prazo.

        Busca tarefas não concluídas com data de vencimento definida e enfileira
        notificações para os usuários ativos da empresa proprietária. Tarefas
        já vencidas geram notificações de checklist atrasado (CHECKLIST_ITEM_OVERDUE),
        enquanto tarefas com prazo dentro da janela de antecedência geram alertas
        de prazo próximo (TASK_DEADLINE).

        Args:
            company: Empresa (tenant) opcional para filtrar tarefas.
            days_threshold: Quantidade de dias futuros para alertar sobre prazos
                próximos (padrão: 3).
            today: Data base de referência. Se omitida, utiliza a data corrente
                da aplicação via timezone.localdate().

        Returns:
            int: Quantidade de tarefas que geraram notificações.
        """
        if today is None:
            today = timezone.localdate()

        tasks = Task.objects.filter(is_completed=False, due_date__isnull=False)
        if company is not None:
            tasks = tasks.filter(company=company)

        tasks = tasks.select_related("company", "wedding").prefetch_related(
            "company__users"
        )

        threshold_date = today + timedelta(days=days_threshold)
        notified_tasks_count = 0

        for task in tasks:
            if task.due_date is None:
                continue

            is_overdue = (
                task.is_overdue
                if today == timezone.localdate()
                else task.due_date < today
            )
            if is_overdue:
                title = "Item de Checklist Vencido"
                notification_type = "CHECKLIST_ITEM_OVERDUE"
                message = (
                    f"A tarefa '{task.title}' está atrasada "
                    f"(vencimento em {task.due_date.strftime('%d/%m/%Y')})."
                )
            elif today <= task.due_date <= threshold_date:
                title = "Prazo de Tarefa Próximo"
                notification_type = "TASK_DEADLINE"
                message = (
                    f"A tarefa '{task.title}' vence em "
                    f"{task.due_date.strftime('%d/%m/%Y')}."
                )
            else:
                continue

            active_users = [u for u in task.company.users.all() if u.is_active]
            if not active_users:
                continue

            wedding_id = task.wedding.uuid if task.wedding else None
            wedding_name = task.wedding.display_name if task.wedding else ""
            link = (
                f"/weddings/{task.wedding.uuid}?tab=planning&subtab=checklist"
                if task.wedding
                else ""
            )

            for user in active_users:
                send_notification_async(
                    company_id=task.company.id,
                    user_id=user.id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    link=link,
                    target_type="task",
                    target_id=task.uuid,
                    wedding_id=wedding_id,
                    wedding_name=wedding_name,
                )

            notified_tasks_count += 1

        return notified_tasks_count
