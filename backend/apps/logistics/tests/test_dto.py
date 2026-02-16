from decimal import Decimal
from uuid import uuid4

from apps.logistics.dto import ContractDTO, ItemDTO, SupplierDTO


class TestSupplierDTO:
    def test_mapping_success(self):
        planner_uuid = uuid4()
        validated_data = {
            "name": "Buffet Festança",
            "cnpj": "12.345.678/0001-90",
            "is_active": True,
        }
        dto = SupplierDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.name == "Buffet Festança"
        assert dto.planner_id == planner_uuid

    def test_extra_fields_are_ignored(self):
        """
        Garante que campos extras vindos do Serializer não quebrem o
        DTO (BaseDTO logic).
        """
        planner_uuid = uuid4()
        data_with_extra = {
            "name": "Fornecedor Teste",
            "field_that_does_not_exist": "ignore-me",
        }

        # Não deve levantar TypeError
        dto = SupplierDTO.from_validated_data(planner_uuid, data_with_extra)

        assert dto.name == "Fornecedor Teste"
        assert not hasattr(dto, "field_that_does_not_exist")


class TestContractDTO:
    def test_mapping_success(self):
        planner_uuid = uuid4()
        validated_data = {
            "wedding_id": uuid4(),
            "supplier_id": uuid4(),
            "total_amount": Decimal("15000.00"),
            "description": "Buffet",
            "status": "SIGNED",
        }
        dto = ContractDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )
        assert dto.total_amount == Decimal("15000.00")

    def test_extra_fields_are_ignored(self):
        planner_uuid = uuid4()
        invalid_data = {
            "total_amount": Decimal("100"),
            "wedding_id": uuid4(),
            "supplier_id": uuid4(),
            "description": "X",
            "status": "Y",
            "invalid_attr": True,
        }

        # O BaseDTO filtra o 'invalid_attr', então o DTO é criado com sucesso
        dto = ContractDTO.from_validated_data(planner_uuid, invalid_data)
        assert dto.total_amount == Decimal("100")
        dto = ContractDTO.from_validated_data(planner_uuid, invalid_data)
        assert dto.total_amount == Decimal("100")


# --- TESTES: ITEM DTO ---


class TestItemDTO:
    def test_mapping_success(self):
        """Valida que um dicionário válido é convertido corretamente em ItemDTO."""
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
        assert dto.acquisition_status == "PENDING"

    def test_extra_fields_are_silently_ignored(self):
        """
        Garante que o BaseDTO ignore campos que não existem na dataclass ItemDTO.
        Isso evita que mudanças no Serializer quebrem a camada de Serviço.
        """
        planner_uuid = uuid4()
        data_with_noise = {
            "name": "Cadeira Individual",
            "wedding_id": uuid4(),
            "budget_category_id": uuid4(),
            "ghost_field": "boo",  # Campo extra que deve ser ignorado
            "unwanted_metadata": {"id": 123},  # Outro campo lixo
        }

        # Com o BaseDTO, isso NÃO deve levantar TypeError
        dto = ItemDTO.from_validated_data(planner_uuid, data_with_noise)

        assert dto.name == "Cadeira Individual"
        # Verificamos que o objeto não possui o campo extra
        assert not hasattr(dto, "ghost_field")
        assert not hasattr(dto, "unwanted_metadata")
