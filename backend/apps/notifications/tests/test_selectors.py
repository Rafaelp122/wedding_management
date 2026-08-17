"""
Testes unitários e de integração para os seletores e managers de Notificações.
"""

from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.notifications.managers import NotificationQuerySet
from apps.notifications.models import Notification
from apps.notifications.selectors import (
    notification_get_selector,
    notification_list_selector,
    notification_unread_count_selector,
)
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
class TestNotificationQuerySet:
    """Testes dos métodos encadeáveis do NotificationQuerySet."""

    def test_for_user_filters_by_user(self, user: Any) -> None:
        other_user = UserFactory(company=user.company)
        n1 = NotificationFactory(user=user)
        NotificationFactory(user=other_user)

        qs = Notification.objects.for_tenant(user.company).for_user(user)
        assert qs.count() == 1
        first_1 = qs.first()
        assert first_1 is not None and first_1.id == n1.id

    def test_unread_filters_is_read_false(self, user: Any) -> None:
        n_unread = NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        qs = Notification.objects.for_tenant(user.company).for_user(user).unread()
        assert qs.count() == 1
        first_unread = qs.first()
        assert first_unread is not None and first_unread.id == n_unread.id

    def test_read_filters_is_read_true(self, user: Any) -> None:
        NotificationFactory(user=user, is_read=False)
        n_read = NotificationFactory(user=user, is_read=True)

        qs = Notification.objects.for_tenant(user.company).for_user(user).read()
        assert qs.count() == 1
        first_read = qs.first()
        assert first_read is not None and first_read.id == n_read.id

    def test_recent_orders_by_created_at_desc(self, user: Any) -> None:
        n1 = NotificationFactory(user=user)
        n2 = NotificationFactory(user=user)

        qs = Notification.objects.for_tenant(user.company).for_user(user).recent()
        items = list(qs)
        assert items[0].id == n2.id
        assert items[1].id == n1.id

    def test_with_wedding_name_annotation(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        NotificationFactory(user=user, wedding_id=wedding.uuid)

        qs = (
            Notification.objects.for_tenant(user.company)
            .for_user(user)
            .with_wedding_name()
        )
        first = qs.first()
        assert first is not None
        assert getattr(first, "wedding_name", None) == (
            f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )

    def test_chaining_methods(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        NotificationFactory(user=user, wedding_id=wedding.uuid, is_read=False)
        NotificationFactory(user=user, is_read=True)

        qs: NotificationQuerySet = (
            Notification.objects.for_tenant(user.company)
            .for_user(user)
            .unread()
            .with_wedding_name()
            .recent()
        )
        assert qs.count() == 1
        item = qs.first()
        assert item is not None
        assert getattr(item, "wedding_name", None) == (
            f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )


@pytest.mark.django_db
class TestNotificationListSelector:
    """Testes do seletor notification_list_selector."""

    def test_list_notifications_success(self, user: Any) -> None:
        n1 = NotificationFactory(user=user, is_read=False)
        n2 = NotificationFactory(user=user, is_read=True)

        qs = notification_list_selector(company=user.company, user=user)
        assert qs.count() == 2
        ids = {item.id for item in qs}
        assert n1.id in ids
        assert n2.id in ids

    def test_list_notifications_unread_only(self, user: Any) -> None:
        n1 = NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        qs = notification_list_selector(
            company=user.company, user=user, unread_only=True
        )
        assert qs.count() == 1
        first_un = qs.first()
        assert first_un is not None and first_un.id == n1.id

    def test_list_notifications_multitenant_isolation(self, user: Any) -> None:
        other_user = UserFactory()
        NotificationFactory(user=user)
        NotificationFactory(user=other_user)

        qs = notification_list_selector(company=user.company, user=user)
        assert qs.count() == 1
        first_user = qs.first()
        assert first_user is not None and first_user.user == user

    def test_list_notifications_wedding_name_annotation(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        NotificationFactory(user=user, wedding_id=wedding.uuid)

        qs = notification_list_selector(company=user.company, user=user)
        first = qs.first()
        assert first is not None
        assert getattr(first, "wedding_name", None) == (
            f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )


@pytest.mark.django_db
class TestNotificationUnreadCountSelector:
    """Testes do seletor notification_unread_count_selector."""

    def test_unread_count_success(self, user: Any) -> None:
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=False)
        NotificationFactory(user=user, is_read=True)

        count = notification_unread_count_selector(company=user.company, user=user)
        assert count == 2

    def test_unread_count_tenant_isolation(self, user: Any) -> None:
        other_user = UserFactory()
        NotificationFactory(user=other_user, is_read=False)

        count = notification_unread_count_selector(company=user.company, user=user)
        assert count == 0


@pytest.mark.django_db
class TestNotificationGetSelector:
    """Testes do seletor notification_get_selector."""

    def test_get_notification_success(self, user: Any) -> None:
        wedding = WeddingFactory(company=user.company)
        n = NotificationFactory(user=user, wedding_id=wedding.uuid)

        result = notification_get_selector(company=user.company, user=user, uuid=n.uuid)
        assert result.id == n.id
        assert getattr(result, "wedding_name", None) == (
            f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
        )

    def test_get_notification_not_found(self, user: Any) -> None:
        with pytest.raises(ObjectNotFoundError):
            notification_get_selector(company=user.company, user=user, uuid=uuid4())

    def test_get_notification_other_user_raises_not_found(self, user: Any) -> None:
        other_user = UserFactory(company=user.company)
        n = NotificationFactory(user=other_user)

        with pytest.raises(ObjectNotFoundError):
            notification_get_selector(company=user.company, user=user, uuid=n.uuid)

    def test_get_notification_other_tenant_raises_not_found(self, user: Any) -> None:
        other_company = CompanyFactory()
        n = NotificationFactory(company=other_company)

        with pytest.raises(ObjectNotFoundError):
            notification_get_selector(company=user.company, user=user, uuid=n.uuid)
