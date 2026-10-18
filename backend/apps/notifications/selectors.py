"""
Seletores de leitura para o domínio de Notificações.
"""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from apps.core.exceptions import ObjectNotFoundError
from apps.notifications.models import Notification


if TYPE_CHECKING:
    from apps.notifications.managers import NotificationQuerySet
    from apps.tenants.models import Company
    from apps.users.models import User


def notification_list_selector(
    *,
    company: Company,
    user: User,
    unread_only: bool = False,
) -> NotificationQuerySet:
    """Retorna o queryset de notificações de um usuário no tenant.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)
    """
    qs: NotificationQuerySet = (
        Notification.objects.for_tenant(company)
        .for_user(user)
        .with_wedding_name()
        .recent()
    )
    if unread_only:
        qs = qs.unread()
    return qs


def notification_unread_count_selector(*, company: Company, user: User) -> int:
    """Retorna a contagem de notificações não lidas de um usuário no tenant.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)
    """
    return int(Notification.objects.for_tenant(company).for_user(user).unread().count())


def notification_get_selector(
    *,
    company: Company,
    user: User,
    uuid: UUID | str,
) -> Notification:
    """Recupera uma notificação específica garantindo isolamento de tenant e usuário.

    Decisão Arquitetural: [ADR-016](docs/architecture/adr/016-pragmatic-multi-tenancy.md)

    Raises:
        ObjectNotFoundError: Se a notificação não for encontrada no tenant para o usuário.
    """
    notification = (
        Notification.objects.for_tenant(company)
        .for_user(user)
        .with_wedding_name()
        .filter(uuid=uuid)
        .first()
    )
    if not notification:
        raise ObjectNotFoundError(
            detail=f"Notificação com UUID '{uuid}' não encontrada."
        )
    return notification
