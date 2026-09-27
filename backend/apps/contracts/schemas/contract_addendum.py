"""
Schemas Pydantic/Ninja para a entidade de Termo Aditivo Contratual (ContractAddendum).
"""

from __future__ import annotations

import datetime
from datetime import date
from decimal import Decimal
from typing import Any, cast

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class ContractAddendumIn(Schema):
    """Schema de entrada para criação de aditivo contratual."""

    model_config = ConfigDict(str_strip_whitespace=True)

    amount: Decimal = Field(gt=0, description="Valor positivo do aditivo")
    justification: str = Field(
        min_length=1, description="Justificativa formal do aditivo"
    )
    signed_date: date | None = None
    pdf_file_key: str | None = None


class ContractAddendumSignIn(Schema):
    """Schema de entrada para formalização da assinatura do aditivo."""

    model_config = ConfigDict(str_strip_whitespace=True)

    signed_date: date | None = None


class ContractAddendumOut(Schema):
    """Schema de saída para representação de termo aditivo."""

    uuid: UUID4
    contract_id: UUID4 = Field(alias="contract.uuid")
    amount: Decimal
    signed_date: date | None = None
    justification: str
    status: str
    has_file: bool = False
    file_name: str | None = None
    created_at: datetime.datetime
    updated_at: datetime.datetime

    @staticmethod
    def resolve_contract_id(obj: Any) -> UUID4:
        return cast(UUID4, obj.contract.uuid)

    @staticmethod
    def resolve_has_file(obj: Any) -> bool:
        return bool(obj.pdf_file)

    @staticmethod
    def resolve_file_name(obj: Any) -> str | None:
        if obj.pdf_file and obj.pdf_file.name:
            return str(obj.pdf_file.name.split("/")[-1])
        return None
