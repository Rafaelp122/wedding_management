import datetime
from decimal import Decimal
from enum import StrEnum
from typing import TYPE_CHECKING

from ninja import Field, Schema
from pydantic import UUID4


if TYPE_CHECKING:
    from apps.weddings.models import Wedding


class WeddingStatusEnum(StrEnum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELED = "CANCELED"


class WeddingIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    groom_name: str = Field(..., min_length=1, max_length=100)
    bride_name: str = Field(..., min_length=1, max_length=100)
    date: datetime.date
    location: str = Field(..., min_length=1, max_length=255)
    expected_guests: int | None = Field(None, ge=1)
    template: str | None = Field(None, max_length=50)


class WeddingPatchIn(Schema):
    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    groom_name: str | None = Field(None, min_length=1, max_length=100)
    bride_name: str | None = Field(None, min_length=1, max_length=100)
    date: datetime.date | None = None
    location: str | None = Field(None, min_length=1, max_length=255)
    expected_guests: int | None = Field(None, ge=1)
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
    allowed_transitions: list[str] = Field(default_factory=list)
    can_complete: bool = False

    @staticmethod
    def resolve_allowed_transitions(obj: "Wedding") -> list[str]:
        return [
            t.value if hasattr(t, "value") else str(t)
            for t in obj.ALLOWED_TRANSITIONS.get(obj.status, [])
        ]

    @staticmethod
    def resolve_can_complete(obj: "Wedding") -> bool:
        if hasattr(obj, "can_transition_to"):
            return obj.can_transition_to(WeddingStatusEnum.COMPLETED)
        return False


class WeddingLookupOut(Schema):
    uuid: UUID4
    groom_name: str
    bride_name: str


class WeddingByMonthOut(Schema):
    month: int = Field(..., ge=1, le=12)
    count: int = Field(..., ge=0)
