"""
Schemas Ninja/Pydantic para validação e serialização de clientes.
"""

from __future__ import annotations

import datetime

from ninja import Field, Schema
from pydantic import UUID4


class ClientIn(Schema):
    """Schema para criação de um novo cliente."""

    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    name: str = Field(..., min_length=1, max_length=255, description="Nome Completo")
    cpf: str = Field(default="", max_length=14, description="CPF do cliente")
    email: str = Field(default="", max_length=255, description="E-mail de contato")
    phone: str = Field(default="", max_length=20, description="Telefone com DDD")
    notes: str = Field(default="", description="Observações cadastrais")


class ClientPatchIn(Schema):
    """Schema para atualização parcial de um cliente existente."""

    model_config = {"extra": "ignore", "str_strip_whitespace": True}

    name: str | None = Field(
        default=None, min_length=1, max_length=255, description="Nome Completo"
    )
    cpf: str | None = Field(default=None, max_length=14, description="CPF do cliente")
    email: str | None = Field(
        default=None, max_length=255, description="E-mail de contato"
    )
    phone: str | None = Field(
        default=None, max_length=20, description="Telefone com DDD"
    )
    notes: str | None = Field(default=None, description="Observações cadastrais")


class ClientOut(Schema):
    """Schema de saída para representação de cliente."""

    uuid: UUID4
    name: str
    cpf: str = ""
    email: str = ""
    phone: str = ""
    notes: str = ""
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ClientListParams(Schema):
    """Parâmetros de filtro para listagem de clientes."""

    q: str = Field(
        default="", description="Termo de busca por nome, CPF, e-mail ou telefone"
    )


class PagedClientOut(Schema):
    """Envelope paginado de clientes."""

    items: list[ClientOut]
    count: int
