"""Módulo de schemas para o domínio de notificações (Notifications)."""

from apps.notifications.schemas.bulk import (
    BulkNotificationIdsIn,
    BulkOperationOut,
)
from apps.notifications.schemas.notification import (
    MarkAllReadOut,
    NotificationOut,
    UnreadCountOut,
)


__all__ = [
    "BulkNotificationIdsIn",
    "BulkOperationOut",
    "MarkAllReadOut",
    "NotificationOut",
    "UnreadCountOut",
]
