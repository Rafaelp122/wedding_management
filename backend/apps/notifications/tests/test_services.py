from typing import Any, cast
from unittest.mock import patch
from uuid import uuid4

import pytest
from django.tasks import Task
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.notifications.models import Notification, NotificationType
from apps.notifications.selectors import (
    notification_list_selector,
    notification_unread_count_selector,
)
from apps.notifications.services import NotificationService
from apps.notifications.tests.factories import (
    NotificationFactory as _NotificationFactory,
)
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def NotificationFactory(*args: Any, **kwargs: Any) -> Notification:
    return cast(Notification, _NotificationFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestNotificationServiceCreate:
    """Testes para o método create_notification e notify."""

    def test_create_notification_success(self, user: Any) -> None:
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

    def test_notify_alias_success(self, user: Any) -> None:
        notification = NotificationService.notify(
            company=user.company,
            user=user,
            title="Título Notify",
            message="Mensagem notify",
            notification_type=NotificationType.GENERAL,
        )
        assert notification.id is not None
        assert notification.title == "Título Notify"

    def test_create_notification_with_target_fields(self, user: Any) -> None:
        target_uuid = uuid4()
        wedding_uuid = uuid4()

        notification = NotificationService.create_notification(
            company=user.company,
            user=user,
            title="Título com Alvo",
            message="Mensagem detalhada",
            notification_type=NotificationType.OVERDUE_INSTALLMENT,
            link="/weddings",
            target_type="installment",
            target_id=target_uuid,
            wedding_id=wedding_uuid,
        )

        assert notification.target_type == "installment"
        assert notification.target_id == target_uuid
        assert notification.wedding_id == wedding_uuid

    def test_create_notification_with_company_and_user_ids(self, user: Any) -> None:
        notification_by_id = NotificationService.create_notification(
            company=user.company.id,
            user=user.id,
            title="Title ID",
            message="Message ID",
        )
        assert notification_by_id.company == user.company
        assert notification_by_id.user == user

        notification_by_uuid = NotificationService.create_notification(
            company=user.company.uuid,
            user=user.uuid,
            title="Title UUID",
            message="Message UUID",
        )
        assert notification_by_uuid.company == user.company
        assert notification_by_uuid.user == user

    def test_create_notification_failure_invalid_user_id(self, user: Any) -> None:
        with pytest.raises(User.DoesNotExist):
            NotificationService.create_notification(
                company=user.company,
                user=999999,
                title="Título",
                message="Mensagem",
            )

    def test_create_notification_failure_user_company_mismatch(self, user: Any) -> None:
        other_company = CompanyFactory()
        with pytest.raises(
            BusinessRuleViolation, match=r"Usuário não pertence à empresa informada\."
        ):
            NotificationService.create_notification(
                company=other_company,
                user=user,
                title="Título",
                message="Mensagem",
            )

    def test_notification_str_representation(self, user: Any) -> None:
        notification = NotificationFactory(
            user=user, title="Novo Evento", type=NotificationType.GENERAL
        )
        assert str(notification) == f"[GENERAL] Novo Evento (user_id={user.id})"


@pytest.mark.django_db
class TestNotificationServiceCreateAsync:
    """Testes para o método create_async_notification."""

    def test_create_async_notification_success(self, user: Any) -> None:
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

    def test_create_async_notification_with_target_fields(self, user: Any) -> None:
        target_uuid = uuid4()
        wedding_uuid = uuid4()

        with patch.object(Task, "enqueue") as mock_enqueue:
            NotificationService.create_async_notification(
                company=user.company,
                user=user,
                title="Async Title",
                message="Async Message",
                notification_type=NotificationType.GENERAL,
                target_type="installment",
                target_id=target_uuid,
                wedding_id=wedding_uuid,
            )

            mock_enqueue.assert_called_once()
            _, kwargs = mock_enqueue.call_args
            assert kwargs["target_type"] == "installment"
            assert kwargs["target_id"] == str(target_uuid)
            assert kwargs["wedding_id"] == str(wedding_uuid)


@pytest.mark.django_db
class TestNotificationServiceMarkAsRead:
    """Testes para o método mark_as_read."""

    def test_mark_as_read_success(self, user: Any) -> None:
        notification = NotificationFactory(user=user, is_read=False)

        updated = NotificationService.mark_as_read(
            user.company, user, notification.uuid
        )
        assert updated.is_read is True
        assert updated.read_at is not None

    def test_mark_as_read_failure_other_tenant(self, user: Any) -> None:
        other_company = CompanyFactory()
        notification = NotificationFactory(company=other_company, is_read=False)

        with pytest.raises(ObjectNotFoundError):
            NotificationService.mark_as_read(user.company, user, notification.uuid)

    def test_mark_as_read_failure_other_user_same_company(self, user: Any) -> None:
        user2 = UserFactory(company=user.company)
        notification = NotificationFactory(
            company=user.company, user=user2, is_read=False
        )

        with pytest.raises(ObjectNotFoundError):
            NotificationService.mark_as_read(user.company, user, notification.uuid)

    def test_mark_as_read_already_read_idempotent(self, user: Any) -> None:
        notification = NotificationFactory(
            user=user, is_read=True, read_at=timezone.now()
        )
        read_at_before = notification.read_at

        updated = NotificationService.mark_as_read(
            user.company, user, notification.uuid
        )
        assert updated.is_read is True
        assert updated.read_at == read_at_before

    def test_mark_as_read_populates_wedding_name(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        notification = NotificationFactory(
            user=user, wedding_id=wedding.uuid, is_read=False
        )

        updated = NotificationService.mark_as_read(
            user.company, user, notification.uuid
        )
        assert (
            updated.wedding_name
            == f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )

    def test_mark_as_read_with_nonexistent_wedding_id(self, user: Any) -> None:
        notification = NotificationFactory(user=user, wedding_id=uuid4(), is_read=False)
        updated = NotificationService.mark_as_read(
            user.company, user, notification.uuid
        )
        assert updated.wedding_name is None


@pytest.mark.django_db
class TestNotificationServiceMarkAllAsRead:
    """Testes para o método mark_all_as_read."""

    def test_mark_all_as_read_success(self, user: Any) -> None:
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        marked_count = NotificationService.mark_all_as_read(user.company, user)
        assert marked_count == 2
        assert notification_unread_count_selector(company=user.company, user=user) == 0

    def test_mark_all_as_read_multitenancy_isolated(self, user: Any) -> None:
        other_user = UserFactory()
        other_note = NotificationFactory(user=other_user, is_read=False)

        marked_count = NotificationService.mark_all_as_read(user.company, user)
        assert marked_count == 0

        other_note.refresh_from_db()
        assert other_note.is_read is False


@pytest.mark.django_db
class TestNotificationServiceDelete:
    """Testes para o método delete_notification."""

    def test_delete_notification_success(self, user: Any) -> None:
        n = NotificationFactory(user=user)
        NotificationService.delete_notification(user.company, user, n.uuid)
        assert notification_list_selector(company=user.company, user=user).count() == 0

    def test_delete_notification_other_user_failure(self, user: Any) -> None:
        other_user = UserFactory(company=user.company)
        n = NotificationFactory(user=other_user)
        with pytest.raises(ObjectNotFoundError):
            NotificationService.delete_notification(user.company, user, n.uuid)


@pytest.mark.django_db
class TestNotificationServiceBulkOperations:
    """Testes para os métodos de operações em lote (bulk)."""

    def test_bulk_mark_as_read_success(self, user: Any) -> None:
        n1 = NotificationFactory(user=user, is_read=False)
        n2 = NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)

        count = NotificationService.bulk_mark_as_read(
            user.company, user, [n1.uuid, n2.uuid]
        )
        assert count == 2
        assert notification_unread_count_selector(company=user.company, user=user) == 1

    def test_bulk_delete_success(self, user: Any) -> None:
        n1 = NotificationFactory(user=user)
        n2 = NotificationFactory(user=user)
        NotificationFactory(user=user)

        count = NotificationService.bulk_delete(user.company, user, [n1.uuid, n2.uuid])
        assert count == 2
        assert notification_list_selector(company=user.company, user=user).count() == 1

    def test_clear_all_success(self, user: Any) -> None:
        NotificationFactory(user=user)
        NotificationFactory(user=user)
        other_user = UserFactory()
        NotificationFactory(user=other_user)

        count = NotificationService.clear_all(user.company, user)
        assert count == 2
        assert notification_list_selector(company=user.company, user=user).count() == 0
        assert (
            notification_list_selector(
                company=other_user.company, user=other_user
            ).count()
            == 1
        )
