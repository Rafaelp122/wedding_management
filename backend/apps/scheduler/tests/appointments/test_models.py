from datetime import timedelta
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.tests.factories import EventFactory as _EventFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def EventFactory(*args: Any, **kwargs: Any) -> Event:
    return cast(Event, _EventFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestEventModelMetadata:
    """Testes de representação e metadados do modelo Event."""

    def test_event_str_is_title(self, user: Any) -> None:
        """__str__ deve retornar o título do evento."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Prova de Vestido")
        assert str(event) == "Prova de Vestido"

    def test_event_ordering_by_start_time(self, user: Any) -> None:
        """Ordenação padrão deve ser por start_time ascendente."""
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        e_late = EventFactory(wedding=wedding, start_time=now + timedelta(days=30))
        e_soon = EventFactory(wedding=wedding, start_time=now + timedelta(days=5))
        e_mid = EventFactory(wedding=wedding, start_time=now + timedelta(days=15))

        events = list(Event.objects.all())
        assert events[0] == e_soon
        assert events[1] == e_mid
        assert events[2] == e_late

    def test_event_end_time_defaults_hour_after_start(self, user: Any) -> None:
        """End_time padrão via factory é 1h após start_time."""
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=now,
            end_time=now + timedelta(hours=1),
        )
        event.full_clean()
        assert event.end_time == now + timedelta(hours=1)


@pytest.mark.django_db
class TestEventTypeChoices:
    """Testes dos tipos de evento disponíveis."""

    def test_event_type_meeting(self, user: Any) -> None:
        """Evento do tipo MEETING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.MEETING)
        event.full_clean()

    def test_event_type_payment(self, user: Any) -> None:
        """Evento do tipo PAYMENT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.PAYMENT)
        event.full_clean()

    def test_event_type_visit(self, user: Any) -> None:
        """Evento do tipo VISIT é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.VISIT)
        event.full_clean()

    def test_event_type_tasting(self, user: Any) -> None:
        """Evento do tipo TASTING é válido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, event_type=Event.TypeChoices.TASTING)
        event.full_clean()

    def test_event_type_default_is_other(self, user: Any) -> None:
        """Tipo padrão deve ser OTHER."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.event_type == Event.TypeChoices.OTHER


@pytest.mark.django_db
class TestEventReminder:
    """Testes das configurações de lembrete do Event."""

    def test_event_reminder_default_disabled(self, user: Any) -> None:
        """reminder_enabled deve ser False por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_enabled is False

    def test_event_reminder_minutes_default(self, user: Any) -> None:
        """reminder_minutes_before deve ser 60 por padrão."""
        wedding = WeddingFactory(user_context=user)
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Teste",
            start_time=timezone.now(),
        )
        assert event.reminder_minutes_before == 60

    def test_event_recurrence_rule_choices(self, user: Any) -> None:
        """RecurrenceChoices contém os valores em português."""
        expected = {"none", "semanal", "quinzenal", "mensal"}
        assert set(Event.RecurrenceChoices.values) == expected


@pytest.mark.django_db
class TestEventRichDomainModel:
    """Testes de invariantes e métodos de domínio do modelo Event."""

    def test_clean_end_time_before_start_time_raises_error(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Evento Inválido",
            start_time=now,
            end_time=now - timedelta(minutes=30),
        )
        with pytest.raises(ValidationError) as exc_info:
            event.clean()
        assert "end_time" in exc_info.value.message_dict
        assert "não pode ser anterior" in str(exc_info.value.message_dict["end_time"])

    def test_clean_valid_interval_passes(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = Event(
            company=user.company,
            wedding=wedding,
            title="Evento Válido",
            start_time=now,
            end_time=now + timedelta(hours=2),
        )
        event.clean()

    def test_semantic_properties(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()

        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            start_time=now,
            end_time=now + timedelta(hours=1, minutes=30),
        )
        assert event.is_payment_event is True

        non_payment = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.MEETING,
            start_time=now,
            end_time=None,
        )
        assert non_payment.is_payment_event is False

    def test_reschedule_valid(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = EventFactory(
            wedding=wedding,
            start_time=now,
            end_time=now + timedelta(hours=1),
        )

        new_start = now + timedelta(days=2)
        new_end = new_start + timedelta(hours=3)
        event.reschedule(new_start, new_end)

        assert event.start_time == new_start
        assert event.end_time == new_end

    def test_reschedule_invalid_raises_error(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()
        event = EventFactory(
            wedding=wedding,
            start_time=now,
            end_time=now + timedelta(hours=1),
        )

        new_start = now + timedelta(days=2)
        new_end = new_start - timedelta(minutes=10)
        with pytest.raises(ValidationError):
            event.reschedule(new_start, new_end)

    def test_payment_event_mutation_blocked(self, user: Any) -> None:
        """BR-S01: Alteração de campos em evento de pagamento é bloqueada no clean()."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            title="Parcela 1/2",
        )
        event.title = "Novo título ilegal"
        with pytest.raises(ValidationError) as exc_info:
            event.clean()
        assert "Eventos de pagamento são gerados automaticamente" in str(exc_info.value)

    def test_convert_to_payment_event_blocked(self, user: Any) -> None:
        """BR-S01: Conversão de outro tipo para PAYMENT é bloqueada no clean()."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.MEETING,
            title="Reunião Inicial",
        )
        event.event_type = Event.TypeChoices.PAYMENT
        with pytest.raises(ValidationError) as exc_info:
            event.clean()
        assert "Não é permitido alterar o tipo de um evento para 'pagamento'" in str(
            exc_info.value
        )

    def test_payment_event_delete_blocked_and_allowed_with_flag(
        self, user: Any
    ) -> None:
        """BR-S01: Exclusão de evento de pagamento é bloqueada sem flag."""
        from apps.core.exceptions import BusinessRuleViolation

        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            title="Parcela 2/2",
        )
        with pytest.raises(BusinessRuleViolation) as exc_info:
            event.delete()
        assert exc_info.value.code == "payment_event_readonly"

        # Com a flag interna, deve permitir exclusão
        event.delete(skip_payment_guard=True)
        assert Event.objects.filter(pk=event.pk).count() == 0


@pytest.mark.django_db
class TestEventReminderOperations:
    """Testes para métodos semânticos de lembrete em Event."""

    def test_enable_and_disable_reminder(self, user: Any) -> None:
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding, reminder_enabled=False, reminder_minutes_before=60
        )

        event.enable_reminder(minutes_before=120)
        assert event.reminder_enabled is True
        assert event.reminder_minutes_before == 120

        event.disable_reminder()
        assert event.reminder_enabled is False
