"""
QuerySet e Manager customizados para o domínio de Notificações.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
    from apps.notifications.models import Notification  # noqa: F401
    from apps.users.models import User


class NotificationQuerySet(TenantQuerySet["Notification"]):
    """QuerySet customizado para Notificações com métodos encadeáveis."""

    def for_user(self, user: User) -> NotificationQuerySet:
        """Filtra as notificações destinadas ao usuário fornecido."""
        return self.filter(user=user)

    def unread(self) -> NotificationQuerySet:
        """Filtra apenas notificações pendentes de leitura (is_read=False)."""
        return self.filter(is_read=False)

    def read(self) -> NotificationQuerySet:
        """Filtra apenas notificações já lidas (is_read=True)."""
        return self.filter(is_read=True)

    def recent(self) -> NotificationQuerySet:
        """Ordena as notificações pelas mais recentes primeiro."""
        return self.order_by("-created_at")

    def with_wedding_name(self) -> NotificationQuerySet:
        """Mantido para compatibilidade fluente.

        O campo wedding_name agora é persistido nativamente na entidade Notification.
        """
        return self

    def mark_as_read(self) -> int:
        """Marca notificações pendentes do queryset como lidas de forma atômica.

        Returns:
            int: Quantidade de registros atualizados.
        """
        from django.utils import timezone

        now = timezone.now()
        return int(self.unread().update(is_read=True, read_at=now, updated_at=now))
