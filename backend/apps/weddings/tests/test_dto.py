from datetime import date
from uuid import uuid4

import pytest

from apps.weddings.dto import WeddingDTO


class TestWeddingDTO:
    def test_wedding_dto_mapping_success(self):
        """Testa mapeamento completo."""
        planner_uuid = uuid4()
        validated_data = {
            "groom_name": "João Silva",
            "bride_name": "Maria Oliveira",
            "date": date(2026, 5, 20),
            "location": "Mansão das Flores",
            "expected_guests": 150,
            "status": "IN_PROGRESS",
        }

        dto = WeddingDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.groom_name == "João Silva"
        assert dto.planner_id == planner_uuid
        assert dto.expected_guests == 150
        assert dto.status == "IN_PROGRESS"

    def test_wedding_dto_default_values(self):
        """Testa aplicação de defaults via BaseDTO."""
        planner_uuid = uuid4()
        validated_data = {
            "groom_name": "Carlos",
            "bride_name": "Ana",
            "date": date(2026, 10, 10),
            "location": "Igreja Matriz",
        }

        dto = WeddingDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        assert dto.expected_guests is None
        assert dto.status == "IN_PROGRESS"

    def test_wedding_dto_type_error_on_missing_required_field(self):
        """
        GARANTIA DE CONTRATO (BaseDTO):
        Como agora usamos o construtor do dataclass, a falta de um campo
        obrigatório resulta em TypeError, não mais KeyError.
        """
        planner_uuid = uuid4()
        # Falta 'location'
        incomplete_data = {
            "groom_name": "João",
            "bride_name": "Maria",
            "date": date(2026, 5, 20),
        }

        # BaseDTO chama cls(**data), que gera TypeError se faltar argumento posicional
        with pytest.raises(TypeError) as excinfo:
            WeddingDTO.from_validated_data(
                user_id=planner_uuid, validated_data=incomplete_data
            )

        assert "location" in str(excinfo.value)
