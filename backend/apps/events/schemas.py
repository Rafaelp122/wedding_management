from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING, Optional, Union

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
    expected_guests: Optional[int] = None  # noqa: UP045


class EventPatchIn(Schema):
    name: Optional[str] = None  # noqa: UP045
    date: Optional[date] = None  # noqa: UP045
    location: Optional[str] = None  # noqa: UP045
    expected_guests: Optional[int] = None  # noqa: UP045
    status: Optional[str] = None  # noqa: UP045


class EventOut(Schema):
    uuid: UUID4
    name: str
    event_type: str
    date: date
    location: str
    expected_guests: Optional[int] = None  # noqa: UP045
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

    wedding_detail: Optional[WeddingDetailOut] = None  # noqa: UP045

    @staticmethod
    def resolve_wedding_detail(obj: Event) -> Optional[WeddingDetail]:  # noqa: UP045
        # Tentamos acessar o related_name definido no OneToOneField
        return getattr(obj, "wedding_detail", None)


# --- POLYMORPHIC TYPES ---

AnyEventOut = Union[WeddingOut, EventOut]  # noqa: UP007
