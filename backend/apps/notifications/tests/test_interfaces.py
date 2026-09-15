"""Testes unitários para as interfaces de Notificações."""

from datetime import date
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from apps.notifications.interfaces import (
    create_notification,
    notify_installment_overdue,
    send_notification_async,
)
from apps.notifications.models import Notification
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestNotificationInterfaces:
    """Valida os contratos da fachada pública de notificações."""

    def test_notify_installment_overdue_enqueues_task(
        self, user: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Garante que notify_installment_overdue enfileira para cada usuário."""
        user2: Any = UserFactory(company=user.company)
        installment_uuid = uuid4()
        wedding_uuid = uuid4()
        mock_task = MagicMock()

        monkeypatch.setattr(
            "apps.notifications.interfaces.dispatch_async_notification_task",
            mock_task,
        )
        monkeypatch.setattr("django.db.transaction.on_commit", lambda fn: fn())

        notify_installment_overdue(
            company=user.company,
            installment_uuid=installment_uuid,
            expense_name="Buffet Premium",
            installment_number=2,
            amount=Decimal("1500.00"),
            due_date=date(2026, 9, 10),
            wedding_uuid=wedding_uuid,
            wedding_name="Casamento de Amanda e Bruno",
            users=[user, user2],
        )

        assert mock_task.enqueue.call_count == 2
        expected_msg = (
            "A parcela 2 de 'Buffet Premium' no valor de "
            "R$ 1500.00 venceu em 10/09/2026."
        )
        mock_task.enqueue.assert_any_call(
            company_id=user.company.id,
            user_id=user.id,
            title="Parcela Vencida",
            message=expected_msg,
            notification_type="OVERDUE_INSTALLMENT",
            link=f"/weddings/{wedding_uuid}?tab=finances",
            target_type="installment",
            target_id=str(installment_uuid),
            wedding_id=str(wedding_uuid),
            wedding_name="Casamento de Amanda e Bruno",
        )

    def test_notify_installment_overdue_empty_users(
        self, user: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Garante retorno rápido quando não houver usuários informados."""
        mock_task = MagicMock()
        monkeypatch.setattr(
            "apps.notifications.interfaces.dispatch_async_notification_task",
            mock_task,
        )

        notify_installment_overdue(
            company=user.company,
            installment_uuid=uuid4(),
            expense_name="Decoração",
            installment_number=1,
            amount=Decimal("500.00"),
            due_date=date(2026, 9, 1),
            users=[],
        )
        mock_task.enqueue.assert_not_called()

    def test_send_notification_async_enqueues_task(
        self, user: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Valida que send_notification_async agenda a task corretamente."""
        target_uuid = uuid4()
        mock_task = MagicMock()

        monkeypatch.setattr(
            "apps.notifications.interfaces.dispatch_async_notification_task",
            mock_task,
        )
        monkeypatch.setattr("django.db.transaction.on_commit", lambda fn: fn())

        send_notification_async(
            company_id=user.company.id,
            user_id=user.id,
            title="Lembrete",
            message="Mensagem de teste",
            notification_type="GENERAL",
            target_type="task",
            target_id=target_uuid,
        )

        mock_task.enqueue.assert_called_once_with(
            company_id=user.company.id,
            user_id=user.id,
            title="Lembrete",
            message="Mensagem de teste",
            notification_type="GENERAL",
            link="",
            target_type="task",
            target_id=str(target_uuid),
            wedding_id=None,
            wedding_name="",
        )

    def test_create_notification_sync(self, user: Any) -> None:
        """Valida a criação e persistência síncrona através da interface."""
        notification = create_notification(
            company=user.company,
            user=user,
            title="Aviso Imediato",
            message="Notificação criada sincronamente.",
            notification_type="GENERAL",
        )

        assert notification.id is not None
        assert Notification.objects.filter(uuid=notification.uuid).exists()
        assert notification.title == "Aviso Imediato"
