from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Union

from ninja import Schema
from pydantic import UUID4, Field


if TYPE_CHECKING:
    from .models import Event, WeddingDetail


# --- BASE EVENT SCHEMAS ---


class EventIn(Schema):
    name: str = Field(..., max_length=255)
    event_type: str = Field(default="WEDDING")
    date: date
    location: str = Field(..., max_length=255)
    expected_guests: int | None = None


class EventPatchIn(Schema):
    name: str | None = None
    date: date | None = None
    location: str | None = None
    expected_guests: int | None = None
    status: str | None = None


class EventOut(Schema):
    uuid: UUID4
    name: str
    event_type: str
    date: date
    location: str
    expected_guests: int | None
    status: str
    created_at: datetime


# --- WEDDING SPECIALIZATION ---


class WeddingDetailIn(Schema):
    groom_name: str = Field(..., max_length=100)
    bride_name: str = Field(..., max_length=100)


class WeddingIn(EventIn):
    """Herda de EventIn e adiciona detalhes do Casamento."""

    wedding_detail: WeddingDetailIn


class WeddingDetailOut(Schema):
    groom_name: str
    bride_name: str


class WeddingOut(EventOut):
    """Herda de EventOut e expõe o detalhe 1:1."""

    wedding_detail: WeddingDetailOut | None = None

    @staticmethod
    def resolve_wedding_detail(obj: Event) -> WeddingDetail | None:
        # Tentamos acessar o related_name definido no OneToOneField
        return getattr(obj, "wedding_detail", None)


# --- POLYMORPHIC TYPES ---

AnyEventOut = Union[WeddingOut, EventOut]
