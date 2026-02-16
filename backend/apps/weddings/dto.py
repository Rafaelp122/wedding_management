from dataclasses import dataclass
from datetime import date
from uuid import UUID

from apps.core.dto import BaseDTO


@dataclass(frozen=True)
class WeddingDTO(BaseDTO):
    """Contrato de dados para criação/edição de casamentos."""

    planner_id: UUID
    groom_name: str
    bride_name: str
    date: date
    location: str
    # Campos com valor padrão DEVEM vir após os obrigatórios
    expected_guests: int | None = None
    status: str = "IN_PROGRESS"

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "WeddingDTO":
        """Mapeia os dados do Serializer injetando o contexto do Planner logado."""
        data = {**validated_data, "planner_id": user_id}
        return cls.from_dict(data)
