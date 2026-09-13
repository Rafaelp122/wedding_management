"""Schemas Pydantic/Ninja para a entidade de Item de Logística (Item)."""

import datetime

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class ItemIn(Schema):
    """Schema de entrada para criação de item de logística."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4 | None = None
    contract: UUID4 | None = None
    name: str = Field(min_length=1, max_length=255)
    description: str = ""
    quantity: int = Field(default=1, gt=0)
    acquisition_status: str = "PENDING"


class ItemStatusTransitionIn(Schema):
    """Schema de entrada para transição de status de aquisição do item."""

    model_config = ConfigDict(str_strip_whitespace=True)

    acquisition_status: str = Field(min_length=1)


class ItemPatchIn(Schema):
    """Schema de entrada para atualização parcial de item de logística."""

    model_config = ConfigDict(str_strip_whitespace=True)

    contract: UUID4 | None = None
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str = ""
    quantity: int | None = Field(default=None, gt=0)
    acquisition_status: str | None = None


class ItemOut(Schema):
    """Schema de saída para exibição de item de logística."""

    uuid: UUID4
    wedding: UUID4 = Field(alias="wedding.uuid")
    contract: UUID4 | None = Field(None, alias="contract.uuid")
    name: str
    description: str
    quantity: int
    acquisition_status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
