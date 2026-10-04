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
    """Retorna o queryset encadeável de notificações de um usuário no tenant.

    Args:
        unread_only: Se True, filtra apenas notificações não lidas.

    Returns:
        QuerySet encadeável anotado com wedding_name e ordenado pelos mais recentes.
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

    Returns:
        Quantidade total de notificações pendentes de leitura.
    """
    return int(Notification.objects.for_tenant(company).for_user(user).unread().count())


def notification_get_selector(
    *,
    company: Company,
    user: User,
    uuid: UUID | str,
) -> Notification:
    """Recupera uma notificação específica garantindo isolamento de tenant e usuário.

    Args:
        uuid: Identificador único da notificação.

    Returns:
        Instância da notificação anotada com wedding_name.

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
        raise ObjectNotFoundError(detail="Notificação não encontrada.")
    return notification
