from datetime import date
from uuid import UUID

from apps.core.dto import BaseDTO


class WeddingDTO(BaseDTO):
    """Contrato de dados para criação/edição de casamentos."""

    planner_id: UUID
    groom_name: str
    bride_name: str
    date: date
    location: str
    expected_guests: int | None = None
    status: str = "IN_PROGRESS"
