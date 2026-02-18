from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BaseDTO(BaseModel):
    """
    Abstração base para DTOs usando Pydantic.
    Garante imutabilidade e limpa dados extras automaticamente.
    """

    # frozen=True: imutável após criação.
    # extra="ignore": ignora campos não definidos na classe
    model_config = ConfigDict(frozen=True, extra="ignore")

    @classmethod
    def from_auth(cls, user_id: UUID, data: dict[str, Any]) -> Self:
        """
        Instancia o DTO injetando o planner_id do contexto de autenticação.
        """
        return cls(**{**data, "planner_id": user_id})
