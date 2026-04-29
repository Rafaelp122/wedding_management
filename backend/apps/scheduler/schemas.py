from datetime import date, datetime

from ninja import Schema
from pydantic import UUID4, Field, model_validator


class AppointmentIn(Schema):
    event: UUID4 | None = None
    title: str = Field(..., max_length=255)
    location: str | None = Field(None, max_length=255)
    description: str | None = None
    event_type: str = Field(..., max_length=50)
    start_time: datetime
    end_time: datetime | None = None

    @model_validator(mode="after")
    def validate_times(self) -> "AppointmentIn":
        if self.start_time and self.end_time and self.end_time < self.start_time:
            raise ValueError(
                "A hora de término não pode ser anterior à hora de início."
            )
        return self


class AppointmentPatchIn(Schema):
    event: UUID4 | None = None
    title: str | None = Field(None, max_length=255)
    location: str | None = Field(None, max_length=255)
    description: str | None = None
    event_type: str | None = Field(None, max_length=50)
    start_time: datetime | None = None
    end_time: datetime | None = None


class AppointmentOut(Schema):
    uuid: UUID4
    company_id: UUID4 = Field(alias="company.uuid")
    event_uuid: UUID4 | None = Field(None, alias="event.uuid")
    title: str
    location: str | None = None
    description: str | None = None
    event_type: str
    start_time: datetime
    end_time: datetime


class TaskIn(Schema):
    event: UUID4
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
    event_uuid: UUID4 = Field(alias="event.uuid")
    title: str
    description: str | None = None
    due_date: date | None = None
    is_completed: bool
