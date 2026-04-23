import datetime

from ninja import Schema
from pydantic import UUID4


class WeddingIn(Schema):
    """
    Schema puro e explícito para CRIAÇÃO de Casamento.
    Desacoplado de Modelos.
    """

    model_config = {"extra": "ignore"}

    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None = None


class WeddingPatchIn(Schema):
    """
    Schema puro e explícito para ATUALIZAÇÃO de Casamento.
    """

    model_config = {"extra": "ignore"}

    groom_name: str | None = None
    bride_name: str | None = None
    date: datetime.date | None = None
    location: str | None = None
    expected_guests: int | None = None


class WeddingOut(Schema):
    """
    Schema de SAÍDA (Response) de Casamento.
    """

    uuid: UUID4
    groom_name: str
    bride_name: str
    date: datetime.date
    location: str
    expected_guests: int | None
    status: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
