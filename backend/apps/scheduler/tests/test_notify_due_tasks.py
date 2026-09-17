"""Testes para o serviço e comando de notificação de prazos de tarefas."""

import io
from datetime import date, timedelta
from typing import Any
from unittest.mock import patch

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.scheduler.services.tasks import TaskService
from apps.scheduler.tests.factories import TaskFactory
from apps.tenants.tests.factories import CompanyFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


FIXED_TODAY = date(2026, 9, 15)


@pytest.mark.django_db
class TestNotifyDueTasksService:
    """Suíte de testes para TaskService.notify_due_tasks."""

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_overdue_task_triggers_checklist_item_overdue(
        self, mock_send: Any, user: Any
    ) -> None:
        """Valida que tarefa atrasada gera CHECKLIST_ITEM_OVERDUE."""
        wedding: Any = WeddingFactory(company=user.company)
        task: Any = TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=2),
            title="Contratar Buffet",
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1

        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["company_id"] == user.company.id
        assert call_kwargs["user_id"] == user.id
        assert call_kwargs["title"] == "Item de Checklist Vencido"
        assert call_kwargs["notification_type"] == "CHECKLIST_ITEM_OVERDUE"
        assert call_kwargs["target_type"] == "task"
        assert call_kwargs["target_id"] == task.uuid
        assert call_kwargs["wedding_id"] == wedding.uuid
        assert (
            call_kwargs["wedding_name"]
            == f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )
        assert task.title in call_kwargs["message"]

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_task_within_threshold_triggers_task_deadline(
        self, mock_send: Any, user: Any
    ) -> None:
        """Valida que tarefa próxima do prazo gera notificação TASK_DEADLINE."""
        wedding: Any = WeddingFactory(company=user.company)
        task: Any = TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY + timedelta(days=2),
            title="Degustação de Doces",
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            days_threshold=3,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1

        call_kwargs = mock_send.call_args.kwargs
        assert call_kwargs["company_id"] == user.company.id
        assert call_kwargs["user_id"] == user.id
        assert call_kwargs["title"] == "Prazo de Tarefa Próximo"
        assert call_kwargs["notification_type"] == "TASK_DEADLINE"
        assert call_kwargs["target_type"] == "task"
        assert call_kwargs["target_id"] == task.uuid
        assert call_kwargs["wedding_id"] == wedding.uuid
        assert (
            call_kwargs["wedding_name"]
            == f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )
        assert task.title in call_kwargs["message"]

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_task_due_today_triggers_task_deadline(
        self, mock_send: Any, user: Any
    ) -> None:
        """Valida que tarefa com vencimento na data corrente gera TASK_DEADLINE."""
        wedding: Any = WeddingFactory(company=user.company)
        task: Any = TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY,
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["notification_type"] == "TASK_DEADLINE"
        assert mock_send.call_args.kwargs["target_id"] == task.uuid

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_task_on_exact_threshold_boundary(self, mock_send: Any, user: Any) -> None:
        """Valida que tarefa no limite exato do threshold gera TASK_DEADLINE."""
        wedding: Any = WeddingFactory(company=user.company)
        task: Any = TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY + timedelta(days=3),
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            days_threshold=3,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["notification_type"] == "TASK_DEADLINE"
        assert mock_send.call_args.kwargs["target_id"] == task.uuid

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_completed_task_is_ignored(self, mock_send: Any, user: Any) -> None:
        """Valida que tarefas concluídas (is_completed=True) são ignoradas."""
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=FIXED_TODAY - timedelta(days=5),
        )
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=True,
            due_date=FIXED_TODAY + timedelta(days=1),
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=FIXED_TODAY,
        )

        assert notified_count == 0
        mock_send.assert_not_called()

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_distant_due_date_task_is_ignored(self, mock_send: Any, user: Any) -> None:
        """Valida que tarefas com vencimento após threshold são ignoradas."""
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY + timedelta(days=10),
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            days_threshold=3,
            today=FIXED_TODAY,
        )

        assert notified_count == 0
        mock_send.assert_not_called()

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_task_without_due_date_is_ignored(self, mock_send: Any, user: Any) -> None:
        """Valida que tarefas sem due_date definido são ignoradas."""
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=None,
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=FIXED_TODAY,
        )

        assert notified_count == 0
        mock_send.assert_not_called()

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_company_isolation_when_company_provided(
        self, mock_send: Any, user: Any
    ) -> None:
        """Valida que apenas tarefas da empresa informada geram alertas."""
        company_a: Any = user.company
        wedding_a: Any = WeddingFactory(company=company_a)
        task_a: Any = TaskFactory(
            wedding=wedding_a,
            company=company_a,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=1),
        )

        company_b: Any = CompanyFactory()
        UserFactory(company=company_b, is_active=True)
        wedding_b: Any = WeddingFactory(company=company_b)
        TaskFactory(
            wedding=wedding_b,
            company=company_b,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=1),
        )

        # Executa filtrando apenas por company_a
        notified_count = TaskService.notify_due_tasks(
            company=company_a,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["company_id"] == company_a.id
        assert mock_send.call_args.kwargs["target_id"] == task_a.uuid

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_global_run_notifies_across_all_companies(self, mock_send: Any) -> None:
        """Valida que sem company, tarefas de todas as empresas são processadas."""
        company_a: Any = CompanyFactory()
        user_a: Any = UserFactory(company=company_a, is_active=True)
        wedding_a: Any = WeddingFactory(company=company_a)
        TaskFactory(
            wedding=wedding_a,
            company=company_a,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=1),
        )

        company_b: Any = CompanyFactory()
        user_b: Any = UserFactory(company=company_b, is_active=True)
        wedding_b: Any = WeddingFactory(company=company_b)
        TaskFactory(
            wedding=wedding_b,
            company=company_b,
            is_completed=False,
            due_date=FIXED_TODAY + timedelta(days=1),
        )

        notified_count = TaskService.notify_due_tasks(
            company=None,
            today=FIXED_TODAY,
        )

        assert notified_count == 2
        assert mock_send.call_count == 2
        notified_users = {call.kwargs["user_id"] for call in mock_send.call_args_list}
        assert notified_users == {user_a.id, user_b.id}

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_only_active_users_are_notified(self, mock_send: Any, user: Any) -> None:
        """Valida que usuários inativos da empresa não recebem notificações."""
        UserFactory(company=user.company, is_active=False)

        wedding: Any = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=1),
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=FIXED_TODAY,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["user_id"] == user.id

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_company_without_active_users_generates_no_notifications(
        self, mock_send: Any
    ) -> None:
        """Valida que empresa sem nenhum usuário ativo não gera notificações."""
        company: Any = CompanyFactory()
        UserFactory(company=company, is_active=False)
        wedding: Any = WeddingFactory(company=company)
        TaskFactory(
            wedding=wedding,
            company=company,
            is_completed=False,
            due_date=FIXED_TODAY - timedelta(days=1),
        )

        notified_count = TaskService.notify_due_tasks(
            company=company,
            today=FIXED_TODAY,
        )

        assert notified_count == 0
        mock_send.assert_not_called()

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_default_today_uses_localdate(self, mock_send: Any, user: Any) -> None:
        """Valida que timezone.localdate() é usado quando today é None."""
        current_today = timezone.localdate()
        wedding: Any = WeddingFactory(company=user.company)
        task: Any = TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=current_today - timedelta(days=1),
        )

        notified_count = TaskService.notify_due_tasks(
            company=user.company,
            today=None,
        )

        assert notified_count == 1
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["target_id"] == task.uuid


@pytest.mark.django_db
class TestNotifyDueTasksCommand:
    """Suíte de testes para o comando de gerenciamento notify_due_tasks."""

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_cli_command_with_due_tasks(self, mock_send: Any, user: Any) -> None:
        """Valida execução do comando CLI quando há tarefas a serem notificadas."""
        current_today = timezone.localdate()
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=current_today - timedelta(days=1),
        )

        out = io.StringIO()
        call_command("notify_due_tasks", stdout=out)

        output = out.getvalue()
        assert "1 tarefa(s) geraram notificações com sucesso." in output
        assert mock_send.call_count == 1

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_cli_command_no_due_tasks(self, mock_send: Any) -> None:
        """Valida execução do comando CLI quando não há tarefas a notificar."""
        out = io.StringIO()
        call_command("notify_due_tasks", stdout=out)

        output = out.getvalue()
        assert "Nenhuma notificação de tarefa necessária." in output
        mock_send.assert_not_called()

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_cli_command_with_custom_threshold(self, mock_send: Any, user: Any) -> None:
        """Valida passagem de argumento --days-threshold no comando CLI."""
        current_today = timezone.localdate()
        wedding = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding,
            company=user.company,
            is_completed=False,
            due_date=current_today + timedelta(days=5),
        )

        # Com threshold padrão (3), não notifica
        out_default = io.StringIO()
        call_command("notify_due_tasks", stdout=out_default)
        assert "Nenhuma notificação de tarefa necessária." in out_default.getvalue()

        # Com threshold estendido (7), notifica
        out_extended = io.StringIO()
        call_command("notify_due_tasks", "--days-threshold=7", stdout=out_extended)
        output_ext = out_extended.getvalue()
        assert "1 tarefa(s) geraram notificações com sucesso." in output_ext

    @patch("apps.scheduler.services.tasks.send_notification_async")
    def test_cli_command_with_company_id(self, mock_send: Any, user: Any) -> None:
        """Valida filtragem por empresa no comando CLI via --company-id."""
        current_today = timezone.localdate()
        wedding_a = WeddingFactory(company=user.company)
        TaskFactory(
            wedding=wedding_a,
            company=user.company,
            is_completed=False,
            due_date=current_today - timedelta(days=1),
        )

        company_b = CompanyFactory()
        UserFactory(company=company_b, is_active=True)
        wedding_b = WeddingFactory(company=company_b)
        TaskFactory(
            wedding=wedding_b,
            company=company_b,
            is_completed=False,
            due_date=current_today - timedelta(days=1),
        )

        out = io.StringIO()
        call_command("notify_due_tasks", f"--company-id={user.company.id}", stdout=out)

        assert "1 tarefa(s) geraram notificações com sucesso." in out.getvalue()
        assert mock_send.call_count == 1
        assert mock_send.call_args.kwargs["company_id"] == user.company.id

    def test_cli_command_with_invalid_company_id(self) -> None:
        """Valida tratamento de erro ao informar ID de empresa inexistente via CLI."""
        out = io.StringIO()
        call_command("notify_due_tasks", "--company-id=999999", stdout=out)

        assert "Empresa com ID 999999 não encontrada." in out.getvalue()
