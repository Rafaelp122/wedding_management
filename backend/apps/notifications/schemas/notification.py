"""Schemas Pydantic/Ninja para a entidade de Notificação (Notification)."""

from datetime import datetime

from ninja import Field, Schema
from pydantic import UUID4


class NotificationOut(Schema):
    """Schema de saída para exibição de notificação."""

    uuid: UUID4
    title: str
    message: str
    type: str
    target_type: str = ""
    target_id: UUID4 | None = None
    wedding_id: UUID4 | None = None
    wedding_name: str | None = None
    is_read: bool
    link: str
    read_at: datetime | None = None
    created_at: datetime


class UnreadCountOut(Schema):
    """Schema de saída para contagem de notificações não lidas."""

    count: int = Field(..., description="Quantidade de notificações não lidas")


class MarkAllReadOut(Schema):
    """Schema de saída para o total de notificações marcadas como lidas."""

    marked_count: int = Field(
        ..., description="Quantidade de notificações marcadas como lidas"
    )
