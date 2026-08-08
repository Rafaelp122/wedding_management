from unittest.mock import patch

import pytest
from django.tasks import Task

from apps.core.exceptions import ObjectNotFoundError
from apps.notifications.models import NotificationType
from apps.notifications.services import NotificationService
from apps.notifications.tests.factories import NotificationFactory
from apps.tenants.tests.factories import CompanyFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestNotificationServiceCreate:
    """Testes para o método create_notification."""

    def test_create_notification_success(self, user):
        notification = NotificationService.create_notification(
            company=user.company,
            user=user,
            title="Título Teste",
            message="Mensagem de teste",
            notification_type=NotificationType.TASK_DEADLINE,
            link="/scheduler/tasks",
        )

        assert notification.id is not None
        assert notification.company == user.company
        assert notification.user == user
        assert notification.title == "Título Teste"
        assert notification.message == "Mensagem de teste"
        assert notification.type == NotificationType.TASK_DEADLINE
        assert notification.link == "/scheduler/tasks"
        assert notification.is_read is False
        assert notification.read_at is None

    def test_create_notification_failure_invalid_user_id(self, user):
        with pytest.raises(User.DoesNotExist):
            NotificationService.create_notification(
                company=user.company,
                user=999999,
                title="Título",
                message="Mensagem",
            )


@pytest.mark.django_db
class TestNotificationServiceCreateAsync:
    """Testes para o método create_async_notification."""

    def test_create_async_notification_success(self, user):
        with patch.object(Task, "enqueue") as mock_enqueue:
            NotificationService.create_async_notification(
                company=user.company,
                user=user,
                title="Async Title",
                message="Async Message",
                notification_type=NotificationType.GENERAL,
            )

            mock_enqueue.assert_called_once()
            _, kwargs = mock_enqueue.call_args
            assert kwargs["company_id"] == user.company.id
            assert kwargs["user_id"] == user.id
            assert kwargs["title"] == "Async Title"
            assert kwargs["message"] == "Async Message"
            assert kwargs["notification_type"] == NotificationType.GENERAL


@pytest.mark.django_db
class TestNotificationServiceList:
    """Testes para o método list_notifications."""

    def test_list_notifications_success(self, user):
        n1 = NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        all_notes = NotificationService.list_notifications(user.company, user)
        assert all_notes.count() == 2

        unread_notes = NotificationService.list_notifications(
            user.company, user, is_read=False
        )
        assert unread_notes.count() == 1
        assert unread_notes.first().id == n1.id

    def test_list_notifications_multitenancy_isolation(self, user):
        other_user = UserFactory()
        NotificationFactory(user=user)
        NotificationFactory(user=other_user)

        user_notes = NotificationService.list_notifications(user.company, user)
        assert user_notes.count() == 1
        assert user_notes.first().user == user


@pytest.mark.django_db
class TestNotificationServiceUnreadCount:
    """Testes para o método get_unread_count."""

    def test_get_unread_count_success(self, user):
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        count = NotificationService.get_unread_count(user.company, user)
        assert count == 2

    def test_get_unread_count_multitenancy_isolated(self, user):
        other_user = UserFactory()
        NotificationFactory(user=other_user, is_read=False)

        count = NotificationService.get_unread_count(user.company, user)
        assert count == 0


@pytest.mark.django_db
class TestNotificationServiceMarkAsRead:
    """Testes para o método mark_as_read."""

    def test_mark_as_read_success(self, user):
        notification = NotificationFactory(user=user, is_read=False)

        updated = NotificationService.mark_as_read(
            user.company, user, notification.uuid
        )
        assert updated.is_read is True
        assert updated.read_at is not None

    def test_mark_as_read_failure_other_tenant(self, user):
        other_company = CompanyFactory()
        notification = NotificationFactory(company=other_company, is_read=False)

        with pytest.raises(ObjectNotFoundError):
            NotificationService.mark_as_read(user.company, user, notification.uuid)

    def test_mark_as_read_failure_other_user_same_company(self, user):
        user2 = UserFactory(company=user.company)
        notification = NotificationFactory(
            company=user.company, user=user2, is_read=False
        )

        with pytest.raises(ObjectNotFoundError):
            NotificationService.mark_as_read(user.company, user, notification.uuid)


@pytest.mark.django_db
class TestNotificationServiceMarkAllAsRead:
    """Testes para o método mark_all_as_read."""

    def test_mark_all_as_read_success(self, user):
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        marked_count = NotificationService.mark_all_as_read(user.company, user)
        assert marked_count == 2
        assert NotificationService.get_unread_count(user.company, user) == 0

    def test_mark_all_as_read_multitenancy_isolated(self, user):
        other_user = UserFactory()
        other_note = NotificationFactory(user=other_user, is_read=False)

        marked_count = NotificationService.mark_all_as_read(user.company, user)
        assert marked_count == 0

        other_note.refresh_from_db()
        assert other_note.is_read is False
