from datetime import timedelta
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.notifications.models import (
    Notification,
    NotificationType,
)
from apps.notifications.tests.factories import (
    NotificationFactory as _NotificationFactory,
)
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory


def NotificationFactory(*args: Any, **kwargs: Any) -> Notification:
    return cast(Notification, _NotificationFactory(*args, **kwargs))


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


@pytest.mark.django_db
class TestNotificationModelMetadata:
    """Testes de representação textual e metadados de Notification."""

    def test_notification_str(self, user: Any) -> None:
        """__str__ deve exibir o tipo, título e user_id."""
        notification = NotificationFactory(
            user=user,
            title="Aviso Importante",
            type=NotificationType.GENERAL,
        )
        assert str(notification) == f"[GENERAL] Aviso Importante (user_id={user.id})"

    def test_notification_ordering(self, user: Any) -> None:
        """Ordenação padrão deve ser decrescente por created_at."""
        n1 = NotificationFactory(user=user, title="Primeira")
        n2 = NotificationFactory(user=user, title="Segunda")

        notifications = list(
            Notification.objects.filter(id__in=[n1.id, n2.id]).order_by("-created_at")
        )
        assert notifications[0] == n2
        assert notifications[1] == n1


@pytest.mark.django_db
class TestNotificationClean:
    """Testes de invariantes e validação no método clean()."""

    def test_clean_raises_validation_error_when_user_company_differs(
        self, user: Any
    ) -> None:
        """clean() deve rejeitar notificação cujo usuário pertence a outra empresa."""
        other_company = CompanyFactory()
        notification = Notification(
            company=other_company,
            user=user,
            title="Notificação Inválida",
            message="Mensagem de teste",
        )

        with pytest.raises(ValidationError) as exc_info:
            notification.clean()

        assert "user" in exc_info.value.message_dict
        assert (
            exc_info.value.message_dict["user"][0]
            == "O usuário destinatário deve pertencer à empresa informada."
        )

    def test_clean_synchronizes_read_at_when_is_read_is_true(self, user: Any) -> None:
        """clean() deve preencher read_at se is_read for True e read_at for None."""
        before = timezone.now()
        notification = Notification(
            company=user.company,
            user=user,
            title="Lida sem data",
            message="Mensagem",
            is_read=True,
            read_at=None,
        )
        notification.clean()
        after = timezone.now()

        assert notification.read_at is not None
        assert before <= notification.read_at <= after

    def test_clean_preserves_existing_read_at_when_is_read_is_true(
        self, user: Any
    ) -> None:
        """clean() não deve sobrescrever read_at se já estiver preenchido."""
        custom_dt = timezone.now() - timedelta(days=2)
        notification = Notification(
            company=user.company,
            user=user,
            title="Lida com data",
            message="Mensagem",
            is_read=True,
            read_at=custom_dt,
        )
        notification.clean()

        assert notification.read_at == custom_dt

    def test_clean_clears_read_at_when_is_read_is_false(self, user: Any) -> None:
        """clean() deve limpar read_at se is_read for False mas read_at
        estiver preenchido."""
        notification = Notification(
            company=user.company,
            user=user,
            title="Não lida com data residual",
            message="Mensagem",
            is_read=False,
            read_at=timezone.now(),
        )
        notification.clean()

        assert notification.read_at is None


@pytest.mark.django_db
class TestNotificationLifecycleMethods:
    """Testes dos métodos semânticos de ciclo de vida de Notification."""

    def test_mark_as_read_sets_is_read_and_read_at(self, user: Any) -> None:
        """mark_as_read() deve definir is_read como True e preencher read_at."""
        notification = NotificationFactory(user=user, is_read=False, read_at=None)

        before = timezone.now()
        notification.mark_as_read()
        after = timezone.now()

        assert notification.is_read is True
        assert notification.read_at is not None
        assert before <= notification.read_at <= after

    def test_mark_as_read_with_custom_timestamp(self, user: Any) -> None:
        """mark_as_read() com parâmetro de data deve usar a data fornecida."""
        notification = NotificationFactory(user=user, is_read=False, read_at=None)
        custom_dt = timezone.now() - timedelta(hours=3)

        notification.mark_as_read(read_at=custom_dt)

        assert notification.is_read is True
        assert notification.read_at == custom_dt

    def test_mark_as_read_is_idempotent(self, user: Any) -> None:
        """mark_as_read() não deve alterar read_at se a notificação já estiver lida."""
        initial_read_at = timezone.now() - timedelta(days=1)
        notification = NotificationFactory(
            user=user, is_read=True, read_at=initial_read_at
        )

        notification.mark_as_read(read_at=timezone.now())

        assert notification.is_read is True
        assert notification.read_at == initial_read_at


@pytest.mark.django_db
class TestNotificationQuerySetMarkAsRead:
    """Testes para o método mark_as_read no NotificationQuerySet."""

    def test_queryset_mark_as_read(self, user: Any) -> None:
        n1 = NotificationFactory(user=user, is_read=False)
        n2 = NotificationFactory(user=user, is_read=False)
        n3 = NotificationFactory(user=user, is_read=True)

        updated_count = Notification.objects.for_user(user).mark_as_read()
        assert updated_count == 2

        n1.refresh_from_db()
        n2.refresh_from_db()
        n3.refresh_from_db()

        assert n1.is_read is True
        assert n1.read_at is not None
        assert n2.is_read is True
        assert n2.read_at is not None
