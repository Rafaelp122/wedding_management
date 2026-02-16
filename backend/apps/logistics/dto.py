from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID

from apps.core.dto import BaseDTO


@dataclass(frozen=True)
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

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "SupplierDTO":
        """Mapeia os dados injetando o planner_id com filtragem automática."""
        data = {**validated_data, "planner_id": user_id}
        return cls.from_dict(data)


@dataclass(frozen=True)
class ContractDTO(BaseDTO):
    """Contrato de dados para a gestão de contratos (RF10, RF13)."""

    planner_id: UUID
    wedding_id: UUID
    supplier_id: UUID
    total_amount: Decimal
    description: str
    status: str
    expiration_date: date | None = None
    alert_days_before: int = 30
    signed_date: date | None = None
    pdf_file: Any | None = None  # Recebe o arquivo enviado via Multipart

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "ContractDTO":
        """Instancia o DTO garantindo a integridade dos campos de auditoria."""
        data = {**validated_data, "planner_id": user_id}
        return cls.from_dict(data)


@dataclass(frozen=True)
class ItemDTO(BaseDTO):
    """Contrato de dados para itens de logística (RF07-RF08)."""

    planner_id: UUID
    wedding_id: UUID
    budget_category_id: UUID
    name: str
    contract_id: UUID | None = None
    description: str | None = ""
    quantity: int = 1
    acquisition_status: str = "PENDING"

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "ItemDTO":
        """Cria o DTO de item vinculando-o ao Planner logado."""
        data = {**validated_data, "planner_id": user_id}
        return cls.from_dict(data)
        return cls.from_dict(data)
