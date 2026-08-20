from typing import Any

from ninja.pagination import paginate
from ninja_extra import Router
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES
from apps.notifications.schemas import (
    BulkNotificationIdsIn,
    BulkOperationOut,
    MarkAllReadOut,
    NotificationOut,
    UnreadCountOut,
)
from apps.notifications.selectors import (
    notification_list_selector,
    notification_unread_count_selector,
)
from apps.notifications.services import NotificationService
from apps.users.types import AuthRequest


notifications_router = Router(tags=["Notifications"])


@notifications_router.get(
    "/",
    response=list[NotificationOut],
    operation_id="notifications_list",
)
@paginate
def list_notifications(request: AuthRequest, is_read: bool | None = None) -> Any:
    """Lista as notificações do usuário logado no tenant atual."""
    user = request.user
    qs = notification_list_selector(
        company=user.company,
        user=user,
        unread_only=(is_read is False),
    )
    if is_read is True:
        qs = qs.read()
    return qs


@notifications_router.get(
    "/unread-count/",
    response=UnreadCountOut,
    operation_id="notifications_unread_count",
)
def get_unread_count(request: AuthRequest) -> UnreadCountOut:
    """Retorna o total de notificações não lidas do usuário logado."""
    user = request.user
    count = notification_unread_count_selector(company=user.company, user=user)
    return UnreadCountOut(count=count)


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


@notifications_router.post(
    "/bulk-read/",
    response={200: BulkOperationOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_bulk_mark_as_read",
)
def bulk_mark_as_read(
    request: AuthRequest, payload: BulkNotificationIdsIn
) -> BulkOperationOut:
    """Marca uma lista de notificações selecionadas como lidas."""
    user = request.user
    count = NotificationService.bulk_mark_as_read(
        company=user.company, user=user, notification_ids=payload.notification_ids
    )
    return BulkOperationOut(affected_count=count)


@notifications_router.post(
    "/bulk-delete/",
    response={200: BulkOperationOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_bulk_delete",
)
def bulk_delete(
    request: AuthRequest, payload: BulkNotificationIdsIn
) -> BulkOperationOut:
    """Exclui uma lista de notificações selecionadas."""
    user = request.user
    count = NotificationService.bulk_delete(
        company=user.company, user=user, notification_ids=payload.notification_ids
    )
    return BulkOperationOut(affected_count=count)


@notifications_router.delete(
    "/clear-all/",
    response={200: BulkOperationOut, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_clear_all",
)
def clear_all(request: AuthRequest) -> BulkOperationOut:
    """Exclui todas as notificações do usuário no tenant atual."""
    user = request.user
    count = NotificationService.clear_all(company=user.company, user=user)
    return BulkOperationOut(affected_count=count)


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


@notifications_router.delete(
    "/{notification_id}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="notifications_delete",
)
def delete_notification(
    request: AuthRequest, notification_id: UUID4
) -> tuple[int, None]:
    """Exclui uma notificação individual do usuário."""
    user = request.user
    NotificationService.delete_notification(
        company=user.company, user=user, notification_id=notification_id
    )
    return 204, None
