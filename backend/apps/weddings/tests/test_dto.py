from datetime import date
from uuid import uuid4

import pytest

from apps.weddings.dto import WeddingDTO


class TestWeddingDTO:
    def test_wedding_dto_mapping_success(self):
        """
        Testa se o DTO mapeia corretamente todos os campos
        enviados pelo Serializer (Mapeamento Explícito).
        """
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
        """
        Testa se o DTO aplica corretamente os valores padrão
        quando campos opcionais não são enviados.
        """
        planner_uuid = uuid4()
        # Simula dados mínimos (sem expected_guests e status)
        validated_data = {
            "groom_name": "Carlos",
            "bride_name": "Ana",
            "date": date(2026, 10, 10),
            "location": "Igreja Matriz",
        }

        dto = WeddingDTO.from_validated_data(
            user_id=planner_uuid, validated_data=validated_data
        )

        # Verifica se o .get() tratou o None e o default do status
        assert dto.expected_guests is None
        assert dto.status == "IN_PROGRESS"

    def test_wedding_dto_key_error_on_missing_required_field(self):
        """
        GARANTIA DE CONTRATO (Mapeamento Explícito):
        Verifica se o DTO estoura KeyError se o Serializer falhar
        em enviar um campo obrigatório.
        """
        planner_uuid = uuid4()
        # Falta o campo obrigatório 'location'
        incomplete_data = {
            "groom_name": "João",
            "bride_name": "Maria",
            "date": date(2026, 5, 20),
        }

        with pytest.raises(KeyError) as excinfo:
            WeddingDTO.from_validated_data(
                user_id=planner_uuid, validated_data=incomplete_data
            )

        assert "location" in str(excinfo.value)
