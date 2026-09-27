import datetime
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
    priority: str = "MEDIUM"
    is_completed: bool = False


class TaskPatchIn(Schema):
    """Schema de entrada para atualização parcial de tarefa."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str = ""
    due_date: date | None = None
    priority: str | None = None
    is_completed: bool | None = None


class TaskOut(Schema):
    """Schema de saída para exibição de tarefa."""

    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    wedding: UUID4 = Field(alias="wedding.uuid")
    title: str
    description: str | None = None
    due_date: date | None = None
    priority: str = "MEDIUM"
    is_completed: bool
    completed_at: datetime.datetime | None = None
    is_overdue: bool = False
    days_overdue: int = 0


# Aliases canônicos alinhados com a RFC-001 (RF-18)
ChecklistItemIn = TaskIn
ChecklistItemPatchIn = TaskPatchIn
ChecklistItemOut = TaskOut


class TimelineCompressionOut(Schema):
    """Schema de saída para análise de compressão da linha do tempo do casamento."""

    model_config = ConfigDict(str_strip_whitespace=True)

    is_timeline_compressed: bool
    compressed_timeline_message: str | None = None
    days_until_wedding: int | None = None
