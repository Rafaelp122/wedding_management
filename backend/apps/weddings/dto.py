from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class WeddingDTO:
    """Contrato de dados para criação/edição de casamentos."""

    planner_id: UUID
    groom_name: str
    bride_name: str
    date: date
    location: str
    expected_guests: int | None
    status: str

    @classmethod
    def from_validated_data(cls, user_id: UUID, validated_data: dict) -> "WeddingDTO":
        """Mapeia os dados do Serializer para o DTO de forma tipada."""
        return cls(
            planner_id=user_id,
            groom_name=validated_data["groom_name"],
            bride_name=validated_data["bride_name"],
            date=validated_data["date"],
            location=validated_data["location"],
            expected_guests=validated_data.get("expected_guests"),
            status=validated_data.get("status", "IN_PROGRESS"),
        )
