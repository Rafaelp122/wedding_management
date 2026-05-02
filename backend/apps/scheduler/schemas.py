from datetime import date, datetime

from ninja import Schema
from pydantic import UUID4, Field, model_validator


class EventIn(Schema):
    wedding: UUID4
    title: str = Field(..., max_length=255)
    location: str | None = Field(None, max_length=255)
    description: str | None = None
    event_type: str = Field(..., max_length=50)
    start_time: datetime
    end_time: datetime | None = None
    reminder_enabled: bool = False
    reminder_minutes_before: int = 60

    @model_validator(mode="after")
    def validate_event(self) -> "EventIn":
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
    wedding: UUID4 | None = None
    title: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    description: str | None = None
    event_type: str | None = Field(None, max_length=50)
    start_time: datetime | None = None
    end_time: datetime | None = None
    reminder_enabled: bool | None = None
    reminder_minutes_before: int | None = None

    @model_validator(mode="after")
    def validate_event(self) -> "EventPatchIn":
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
    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    wedding: UUID4 = Field(alias="wedding.uuid")
    title: str
    location: str | None = None
    description: str | None = None
    event_type: str
    start_time: datetime
    end_time: datetime | None = None
    reminder_enabled: bool
    reminder_minutes_before: int


class TaskIn(Schema):
    wedding: UUID4
    title: str = Field(..., max_length=255)
    description: str | None = None
    due_date: date | None = None
    is_completed: bool = False


class TaskPatchIn(Schema):
    title: str | None = Field(None, max_length=255)
    description: str | None = None
    due_date: date | None = None
    is_completed: bool | None = None


class TaskOut(Schema):
    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    wedding: UUID4 = Field(alias="wedding.uuid")
    title: str
    description: str | None = None
    due_date: date | None = None
    is_completed: bool
