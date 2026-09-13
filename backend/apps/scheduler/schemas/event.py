"""Schemas Pydantic/Ninja para a entidade de Evento/Compromisso (Event)."""

from datetime import datetime

from ninja import Field, Schema
from pydantic import UUID4, ConfigDict, model_validator


class EventIn(Schema):
    """Schema de entrada para criação de evento/compromisso."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4
    title: str = Field(min_length=1, max_length=255)
    location: str = Field(default="", max_length=255)
    description: str = ""
    event_type: str = Field(max_length=50)
    start_time: datetime
    end_time: datetime | None = None
    recurrence_rule: str | None = "none"
    reminder_enabled: bool = False
    reminder_minutes_before: int = 60

    @model_validator(mode="after")
    def validate_event(self) -> "EventIn":
        """Valida horários e minutos de antecedência do lembrete."""
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError(
                "A hora de término não pode ser anterior à hora de início."
            )

        if (
            self.reminder_minutes_before is not None
            and self.reminder_minutes_before < 0
        ):
            raise ValueError("Os minutos do lembrete devem ser um valor positivo.")

        return self


class EventPatchIn(Schema):
    """Schema de entrada para atualização parcial de evento/compromisso."""

    model_config = ConfigDict(str_strip_whitespace=True)

    wedding: UUID4 | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    location: str = Field(default="", max_length=255)
    description: str = ""
    event_type: str | None = Field(default=None, max_length=50)
    start_time: datetime | None = None
    end_time: datetime | None = None
    recurrence_rule: str | None = None
    reminder_enabled: bool | None = None
    reminder_minutes_before: int | None = None

    @model_validator(mode="after")
    def validate_event(self) -> "EventPatchIn":
        """Valida horários e minutos de antecedência do lembrete."""
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError(
                "A hora de término não pode ser anterior à hora de início."
            )

        if (
            self.reminder_minutes_before is not None
            and self.reminder_minutes_before < 0
        ):
            raise ValueError("Os minutos do lembrete devem ser um valor positivo.")
        return self


class EventOut(Schema):
    """Schema de saída para exibição de evento/compromisso."""

    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    wedding: UUID4 = Field(alias="wedding.uuid")
    title: str
    location: str | None = None
    description: str | None = None
    event_type: str
    start_time: datetime
    end_time: datetime | None = None
    recurrence_rule: str
    reminder_enabled: bool
    reminder_minutes_before: int
