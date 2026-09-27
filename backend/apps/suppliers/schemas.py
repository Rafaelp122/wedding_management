"""Schemas Pydantic/Ninja para a entidade de Fornecedor (Supplier)."""

from __future__ import annotations

import datetime
import re

from django.core.exceptions import ValidationError as DjangoValidationError
from ninja import Field, Schema
from pydantic import UUID4, ConfigDict, field_validator

from apps.suppliers.validators import validate_cnpj_modulo11


class SupplierIn(Schema):
    """Schema de entrada para criação de fornecedor."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str
    cnpj: str = Field(default="", max_length=18)
    phone: str
    email: str
    is_active: bool = True
    address: str = ""
    city: str = ""
    state: str = Field(default="", pattern="^$|^[A-Z]{2}$")
    website: str = Field(default="", pattern=r"^(?:https?://\S+)?$")
    notes: str = ""

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str) -> str:
        """Valida se o CNPJ está no formato padrão e obedece ao Módulo 11."""
        if v:
            if not re.match(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$", v):
                raise ValueError(
                    "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.",
                )
            try:
                validate_cnpj_modulo11(v)
            except DjangoValidationError as exc:
                raise ValueError(
                    exc.message if hasattr(exc, "message") else str(exc)
                ) from exc
        return v

    @field_validator("website")
    @classmethod
    def validate_website_format(cls, v: str) -> str:
        """Valida se o website segue o formato de URL HTTP/HTTPS."""
        if v and not re.match(r"^(?:https?://\S+)?$", v):
            raise ValueError("Website deve ser uma URL válida (http:// ou https://).")
        return v


class SupplierPatchIn(Schema):
    """Schema de entrada para atualização parcial de fornecedor."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = None
    cnpj: str | None = Field(default=None, max_length=18)
    phone: str | None = None
    email: str | None = None
    is_active: bool | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = Field(default=None, pattern="^$|^[A-Z]{2}$")
    website: str | None = None
    notes: str | None = None

    @field_validator("cnpj")
    @classmethod
    def validate_cnpj_format(cls, v: str | None) -> str | None:
        """Valida se o CNPJ está no formato padrão e obedece ao Módulo 11 quando fornecido."""
        if v is not None and v != "":
            if not re.match(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$", v):
                raise ValueError(
                    "CNPJ deve estar no formato XX.XXX.XXX/XXXX-XX.",
                )
            try:
                validate_cnpj_modulo11(v)
            except DjangoValidationError as exc:
                raise ValueError(
                    exc.message if hasattr(exc, "message") else str(exc)
                ) from exc
        return v

    @field_validator("website")
    @classmethod
    def validate_website_format(cls, v: str | None) -> str | None:
        """Valida se o website segue o formato de URL HTTP/HTTPS quando fornecido."""
        if v is not None and not re.match(r"^(?:https?://\S+)?$", v):
            raise ValueError("Website deve ser uma URL válida (http:// ou https://).")
        return v


class SupplierOut(Schema):
    """Schema de saída para exibição de fornecedor."""

    uuid: UUID4
    name: str
    cnpj: str
    phone: str
    email: str
    is_active: bool
    address: str = ""
    city: str = ""
    state: str = Field(default="", min_length=0, max_length=2)
    website: str = ""
    notes: str = ""
    created_at: datetime.datetime
    updated_at: datetime.datetime


class PagedSupplierOut(Schema):
    """Envelope paginado de fornecedores."""

    items: list[SupplierOut]
    count: int
