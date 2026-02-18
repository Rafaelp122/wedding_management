from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from pydantic import AliasChoices, Field

from apps.core.dto import BaseDTO


class SupplierDTO(BaseDTO):
    """
    Contrato de dados para fornecedores da logística (RF09).
    """

    planner_id: UUID
    name: str
    cnpj: str | None = None
    phone: str | None = None
    email: str | None = None
    website: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    notes: str | None = None
    is_active: bool = True


class ContractDTO(BaseDTO):
    """
    Contrato de dados para a gestão de contratos (RF10, RF13).
    Mapeia os campos vindos do Serializer para os IDs internos.
    """

    planner_id: UUID
    total_amount: Decimal
    description: str
    status: str
    expiration_date: date | None = None
    alert_days_before: int = 30
    signed_date: date | None = None
    pdf_file: Any | None = None  # Suporta Multipart/Upload

    # Mapeamentos de campos externos para IDs internos
    wedding_id: UUID = Field(validation_alias=AliasChoices("wedding_id", "wedding"))
    supplier_id: UUID = Field(validation_alias=AliasChoices("supplier_id", "supplier"))


class ItemDTO(BaseDTO):
    """
    Contrato de dados para itens de logística (RF07-RF08).
    Garante a integridade dos vínculos com orçamento e contrato.
    """

    planner_id: UUID
    name: str
    description: str | None = ""
    quantity: int = 1
    acquisition_status: str = "PENDING"

    # Mapeamentos para chaves estrangeiras
    wedding_id: UUID = Field(validation_alias=AliasChoices("wedding_id", "wedding"))
    budget_category_id: UUID = Field(
        validation_alias=AliasChoices("budget_category_id", "budget_category")
    )
    contract_id: UUID | None = Field(
        default=None, validation_alias=AliasChoices("contract_id", "contract")
    )
