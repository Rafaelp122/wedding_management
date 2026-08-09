from uuid import uuid4

import pytest

from apps.notifications.models import Notification, NotificationType
from apps.notifications.tasks import dispatch_async_notification_task


@pytest.mark.django_db
class TestNotificationTasks:
    """Testes de integração para as tarefas assíncronas de notificação."""

    def test_dispatch_async_notification_task_with_pk_ids(self, user):
        dispatch_async_notification_task.func(
            company_id=user.company.id,
            user_id=user.id,
            title="Async Task Title",
            message="Async Task Message",
            notification_type=NotificationType.GENERAL,
        )

        notification = Notification.objects.get(user=user, title="Async Task Title")
        assert notification.message == "Async Task Message"
        assert notification.company == user.company

    def test_dispatch_async_notification_task_with_uuids(self, user):
        target_uuid = str(uuid4())
        wedding_uuid = str(uuid4())

        dispatch_async_notification_task.func(
            company_id=str(user.company.uuid),
            user_id=str(user.uuid),
            title="Async UUID Title",
            message="Async UUID Message",
            notification_type=NotificationType.OVERDUE_INSTALLMENT,
            link="/weddings",
            target_type="installment",
            target_id=target_uuid,
            wedding_id=wedding_uuid,
        )

        notification = Notification.objects.get(user=user, title="Async UUID Title")
        assert str(notification.target_id) == target_uuid
        assert str(notification.wedding_id) == wedding_uuid
