from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class SupplierDTO:
    """
    Contrato de dados para fornecedores da logística (RF09).

    Este DTO é o espelho do modelo Supplier para garantir a integridade
    dos dados entre a camada de API e a camada de Serviço.
    """

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
    planner_id: UUID | None = None

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "SupplierDTO":
        """
        Mapeia os dados validados do Serializer para o DTO via unpacking.

        AVISO: Este método assume uma correspondência de 1:1 entre as chaves
        do 'validated_data' e os atributos desta dataclass. Caso o Serializer
        envie campos extras não definidos no DTO, um TypeError será lançado.
        """
        return cls(planner_id=user_id, **validated_data)


@dataclass(frozen=True)
class ContractDTO:
    """Contrato de dados para a gestão de contratos (RF10, RF13)."""

    wedding_id: UUID
    supplier_id: UUID
    total_amount: Decimal
    description: str
    status: str
    expiration_date: date | None = None
    alert_days_before: int = 30
    signed_date: date | None = None
    pdf_file: Any | None = None  # Recebe o arquivo enviado via Multipart
    planner_id: UUID | None = None

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "ContractDTO":
        """
        Mapeia os dados do Serializer para o DTO.
        AVISO: Assume correspondência 1:1. Requer teste de integridade.
        """
        # Extraímos IDs de objetos se o Serializer retornar a instância em vez do ID
        return cls(planner_id=user_id, **validated_data)


@dataclass(frozen=True)
class ItemDTO:
    """Contrato de dados para itens de logística (RF07-RF08)."""

    wedding_id: UUID
    budget_category_id: UUID
    name: str
    contract_id: UUID | None = None
    description: str | None = ""
    quantity: int = 1
    acquisition_status: str = "PENDING"
    planner_id: UUID | None = None

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "ItemDTO":
        """Mapeia os dados do Serializer para o DTO via unpacking."""
        return cls(planner_id=user_id, **validated_data)
