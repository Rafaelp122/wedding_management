import datetime
from decimal import Decimal
from enum import StrEnum

from ninja import Field, Schema
from pydantic import UUID4


class WeddingStatusEnum(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class WeddingIn(Schema):
    model_config = {"extra": "ignore"}

    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None = None
    template: str | None = Field(None, max_length=50)


class WeddingPatchIn(Schema):
    model_config = {"extra": "ignore"}

    groom_name: str | None = None
    bride_name: str | None = None
    date: datetime.date | None = None
    location: str | None = None
    expected_guests: int | None = None
    status: WeddingStatusEnum | None = None


class WeddingOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None
    status: WeddingStatusEnum
    template: str | None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    total_budget: Decimal | None = Field(None, ge=0)
    overdue_installments: int = Field(0, ge=0)
    incomplete_tasks: int = Field(0, ge=0)


class WeddingLookupOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str


class WeddingByMonthOut(Schema):
    month: int = Field(..., ge=1, le=12)
    count: int = Field(..., ge=0)
