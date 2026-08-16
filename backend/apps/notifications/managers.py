"""
QuerySet e Manager customizados para o domínio de Notificações.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import OuterRef, Subquery, Value
from django.db.models.functions import Concat

from apps.tenants.managers import TenantQuerySet


if TYPE_CHECKING:
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
        """Anota cada notificação com o nome formatado do casamento associado."""
        from apps.weddings.models import Wedding

        return self.annotate(
            wedding_name=Subquery(
                Wedding.objects.filter(uuid=OuterRef("wedding_id")).values(
                    name=Concat(
                        Value("Casamento de "),
                        "bride_name",
                        Value(" e "),
                        "groom_name",
                    )
                )[:1]
            )
        )
