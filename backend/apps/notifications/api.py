from typing import Any

from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.notifications.schemas import (
    MarkAllReadOut,
    NotificationOut,
    UnreadCountOut,
)
from apps.notifications.services import NotificationService
from apps.users.types import AuthRequest


notifications_router = Router(tags=["Notifications"])


@notifications_router.get(
    "/",
    response=list[NotificationOut],
    operation_id="notifications_list",
)
def list_notifications(request: AuthRequest, is_read: bool | None = None) -> Any:
    """Lista as notificações do usuário logado no tenant atual."""
    user = request.user
    return NotificationService.list_notifications(
        company=user.company, user=user, is_read=is_read
    )


@notifications_router.get(
    "/unread-count/",
    response=UnreadCountOut,
    operation_id="notifications_unread_count",
)
def get_unread_count(request: AuthRequest) -> UnreadCountOut:
    """Retorna o total de notificações não lidas do usuário logado."""
    user = request.user
    count = NotificationService.get_unread_count(company=user.company, user=user)
    return UnreadCountOut(count=count)


@notifications_router.patch(
    "/{notification_id}/read/",
    response={200: NotificationOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_mark_as_read",
)
def mark_as_read(request: AuthRequest, notification_id: UUID4) -> Any:
    """Marca uma notificação específica como lida."""
    user = request.user
    return NotificationService.mark_as_read(
        company=user.company, user=user, notification_id=notification_id
    )


@notifications_router.post(
    "/read-all/",
    response={200: MarkAllReadOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_mark_all_as_read",
)
def mark_all_as_read(request: AuthRequest) -> MarkAllReadOut:
    """Marca todas as notificações pendentes do usuário como lidas."""
    user = request.user
    marked_count = NotificationService.mark_all_as_read(company=user.company, user=user)
    return MarkAllReadOut(marked_count=marked_count)
