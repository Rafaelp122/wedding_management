"""Schemas Pydantic/Ninja para a entidade de Tarefa (Task)."""

from datetime import date

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict


class TaskIn(Schema):
    """Schema de entrada para criação de tarefa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    title: str = Field(min_length=1, max_length=255)
    description: str = ""
    due_date: date | None = None
    is_completed: bool = False


class TaskPatchIn(Schema):
    """Schema de entrada para atualização parcial de tarefa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str = ""
    due_date: date | None = None
    is_completed: bool | None = None


class TaskOut(Schema):
    """Schema de saída para exibição de tarefa."""

    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    wedding: UUID4 = Field(alias="wedding.uuid")
    title: str
    description: str | None = None
    due_date: date | None = None
    is_completed: bool
