"""Testes unitários para schemas do domínio de agendamento (Scheduler)."""

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

import pytest
from pydantic import ValidationError

from apps.scheduler.schemas import (
    EventIn,
    EventOut,
    EventPatchIn,
    TaskIn,
    TaskOut,
    TaskPatchIn,
)


class Dummy:
    """Objeto simples para simular instâncias de modelos em testes unitários puros."""

    def __init__(self, **kwargs: Any) -> None:
        self.__dict__.update(kwargs)


class TestEventSchemas:
    """Testes de validação para schemas de Evento (Event)."""

    def test_event_in_whitespace_and_validations(self) -> None:
        wedding_id = uuid.uuid4()
        now = datetime.now(UTC)
        schema = EventIn(
            wedding=wedding_id,
            title="   Degustação do Cardápio   ",
            location="   Espaço Buffet Jardim   ",
            description="   Escolha das entradas e pratos principais   ",
            event_type="TASTING",
            start_time=now,
            end_time=now + timedelta(hours=2),
            reminder_minutes_before=30,
        )
        assert schema.title == "Degustação do Cardápio"
        assert schema.location == "Espaço Buffet Jardim"
        assert schema.description == "Escolha das entradas e pratos principais"
        assert schema.reminder_minutes_before == 30

    def test_event_in_rejects_empty_title(self) -> None:
        wedding_id = uuid.uuid4()
        now = datetime.now(UTC)
        with pytest.raises(ValidationError):
            EventIn(
                wedding=wedding_id,
                title="",
                event_type="MEETING",
                start_time=now,
            )

        with pytest.raises(ValidationError):
            EventIn(
                wedding=wedding_id,
                title="   ",
                event_type="MEETING",
                start_time=now,
            )

    def test_event_in_rejects_end_time_before_start_time(self) -> None:
        wedding_id = uuid.uuid4()
        now = datetime.now(UTC)
        with pytest.raises(ValidationError) as exc:
            EventIn(
                wedding=wedding_id,
                title="Reunião com Fotógrafo",
                event_type="MEETING",
                start_time=now,
                end_time=now - timedelta(minutes=30),
            )
        assert "A hora de término não pode ser anterior à hora de início" in str(
            exc.value
        )

    def test_event_in_rejects_negative_reminder_minutes(self) -> None:
        wedding_id = uuid.uuid4()
        now = datetime.now(UTC)
        with pytest.raises(ValidationError) as exc:
            EventIn(
                wedding=wedding_id,
                title="Reunião",
                event_type="MEETING",
                start_time=now,
                reminder_minutes_before=-10,
            )
        assert "Os minutos do lembrete devem ser um valor positivo" in str(exc.value)

    def test_event_patch_in_validations(self) -> None:
        now = datetime.now(UTC)
        schema = EventPatchIn(
            title="   Novo Título   ",
            start_time=now,
            end_time=now + timedelta(hours=1),
        )
        assert schema.title == "Novo Título"

        with pytest.raises(ValidationError):
            EventPatchIn(title="")

        with pytest.raises(ValidationError):
            EventPatchIn(
                start_time=now,
                end_time=now - timedelta(minutes=10),
            )

        with pytest.raises(ValidationError):
            EventPatchIn(reminder_minutes_before=-5)

    def test_event_out_serialization_pure(self) -> None:
        event_uuid = uuid.uuid4()
        company_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()
        now = datetime.now(UTC)

        mock_event = Dummy(
            uuid=event_uuid,
            company=Dummy(uuid=company_uuid),
            wedding=Dummy(uuid=wedding_uuid),
            title="Cerimônia",
            location="Igreja Matriz",
            description="Entrada dos noivos",
            event_type="CEREMONY",
            start_time=now,
            end_time=now + timedelta(hours=1),
            recurrence_rule="none",
            reminder_enabled=True,
            reminder_minutes_before=60,
        )

        out = EventOut.from_orm(mock_event)
        assert out.uuid == event_uuid
        assert out.company_id == company_uuid
        assert out.wedding == wedding_uuid
        assert out.title == "Cerimônia"
        assert out.event_type == "CEREMONY"


class TestTaskSchemas:
    """Testes de validação para schemas de Tarefa (Task)."""

    def test_task_in_whitespace_and_validations(self) -> None:
        wedding_id = uuid.uuid4()
        schema = TaskIn(
            wedding=wedding_id,
            title="   Contratar assessoria de casamento   ",
            description="   Pesquisar 3 opções de fornecedores   ",
            due_date=date(2026, 12, 31),
        )
        assert schema.title == "Contratar assessoria de casamento"
        assert schema.description == "Pesquisar 3 opções de fornecedores"
        assert schema.is_completed is False

    def test_task_in_rejects_empty_title(self) -> None:
        wedding_id = uuid.uuid4()
        with pytest.raises(ValidationError):
            TaskIn(wedding=wedding_id, title="")

        with pytest.raises(ValidationError):
            TaskIn(wedding=wedding_id, title="   ")

    def test_task_patch_in_validations(self) -> None:
        schema = TaskPatchIn(
            title="   Comprar alianças   ",
            is_completed=True,
        )
        assert schema.title == "Comprar alianças"
        assert schema.is_completed is True

        with pytest.raises(ValidationError):
            TaskPatchIn(title="")

    def test_task_out_serialization_pure(self) -> None:
        task_uuid = uuid.uuid4()
        company_uuid = uuid.uuid4()
        wedding_uuid = uuid.uuid4()

        mock_task = Dummy(
            uuid=task_uuid,
            company=Dummy(uuid=company_uuid),
            wedding=Dummy(uuid=wedding_uuid),
            title="Enviar convites",
            description="Enviar convites via correio",
            due_date=date(2026, 8, 1),
            is_completed=False,
            is_overdue=True,
            days_overdue=5,
        )

        out = TaskOut.from_orm(mock_task)
        assert out.uuid == task_uuid
        assert out.company_id == company_uuid
        assert out.wedding == wedding_uuid
        assert out.title == "Enviar convites"
        assert out.is_completed is False
        assert out.is_overdue is True
        assert out.days_overdue == 5
