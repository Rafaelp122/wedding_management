from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest

from apps.logistics.dto import ContractDTO, ItemDTO, SupplierDTO


# --- TESTES: SUPPLIER DTO ---


class TestSupplierDTO:
    def test_mapping_success(self):
        planner_uuid = uuid4()
        validated_data = {
            "name": "Buffet Festança",
            "cnpj": "12.345.678/0001-90",
            "phone": "(11) 99999-9999",
            "email": "contato@festanca.com",
            "is_active": True,
        }

        dto = SupplierDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.name == "Buffet Festança"
        assert dto.planner_id == planner_uuid
        assert dto.is_active is True

    def test_integrity_violation(self):
        planner_uuid = uuid4()
        invalid_data = {"name": "X", "extra_field": "error"}

        with pytest.raises(TypeError) as excinfo:
            SupplierDTO.from_validated_data(planner_uuid, invalid_data)
        assert "unexpected keyword argument 'extra_field'" in str(excinfo.value)


# --- TESTES: CONTRACT DTO ---


class TestContractDTO:
    def test_mapping_success(self):
        planner_uuid = uuid4()
        validated_data = {
            "wedding_id": uuid4(),
            "supplier_id": uuid4(),
            "total_amount": Decimal("15000.00"),
            "description": "Contrato de Buffet Completo",
            "status": "SIGNED",
            "signed_date": date(2026, 5, 20),
            "pdf_file": None,
        }

        dto = ContractDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.total_amount == Decimal("15000.00")
        assert dto.planner_id == planner_uuid
        assert dto.status == "SIGNED"

    def test_integrity_violation(self):
        planner_uuid = uuid4()
        invalid_data = {"total_amount": Decimal("100"), "invalid_attr": True}

        with pytest.raises(TypeError) as excinfo:
            ContractDTO.from_validated_data(planner_uuid, invalid_data)
        assert "unexpected keyword argument 'invalid_attr'" in str(excinfo.value)


# --- TESTES: ITEM DTO ---


class TestItemDTO:
    def test_mapping_success(self):
        planner_uuid = uuid4()
        validated_data = {
            "wedding_id": uuid4(),
            "budget_category_id": uuid4(),
            "name": "Cadeiras Tiffany",
            "quantity": 200,
            "acquisition_status": "PENDING",
        }

        dto = ItemDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.name == "Cadeiras Tiffany"
        assert dto.quantity == 200
        assert dto.planner_id == planner_uuid

    def test_integrity_violation(self):
        planner_uuid = uuid4()
        invalid_data = {"name": "Cadeira", "ghost_field": "boo"}

        with pytest.raises(TypeError) as excinfo:
            ItemDTO.from_validated_data(planner_uuid, invalid_data)
        assert "unexpected keyword argument 'ghost_field'" in str(excinfo.value)
