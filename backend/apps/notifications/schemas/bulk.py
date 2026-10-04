"""Schemas Pydantic/Ninja para operações em lote de notificações."""

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class BulkNotificationIdsIn(Schema):
    model_config = ConfigDict(str_strip_whitespace=True)

    notification_ids: list[UUID4] = Field(
        ..., min_length=1, description="Lista de UUIDs de notificações"
    )


class BulkOperationOut(Schema):
    affected_count: int = Field(..., description="Quantidade de registros afetados")
