from datetime import datetime

from ninja import Schema
from pydantic import UUID4, Field


class NotificationOut(Schema):
    uuid: UUID4
    title: str
    message: str
    type: str
    is_read: bool
    link: str
    read_at: datetime | None = None
    created_at: datetime


class UnreadCountOut(Schema):
    count: int = Field(..., description="Quantidade de notificações não lidas")


class MarkAllReadOut(Schema):
    marked_count: int = Field(
        ..., description="Quantidade de notificações marcadas como lidas"
    )
