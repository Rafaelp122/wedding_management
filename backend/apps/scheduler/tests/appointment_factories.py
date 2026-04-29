"""
Fábricas do Agendamento (Scheduler Factories).
"""

from datetime import timedelta
from typing import Any

import factory
from django.utils import timezone

from apps.events.tests.factories import EventFactory
from apps.scheduler.models.appointment import Appointment
from apps.scheduler.models.task import Task


class AppointmentFactory(factory.django.DjangoModelFactory):
    """Fábrica para Compromissos (Appointments)."""

    class Meta:
        model = Appointment

    # Um compromisso pode estar vinculado a um Evento (Casamento, etc)
    event = factory.SubFactory(EventFactory)
    company = factory.SelfAttribute("event.company")

    title: Any = factory.Faker("sentence", nb_words=4)
    location = factory.Faker("address")
    description = factory.Faker("paragraph")

    event_type: Any = factory.Iterator(
        [
            Appointment.EventType.MEETING,
            Appointment.EventType.VISIT,
            Appointment.EventType.DEGUSTATION,
            Appointment.EventType.OTHER,
        ]
    )

    start_time = factory.Faker(
        "future_datetime", tzinfo=timezone.get_current_timezone()
    )

    @factory.lazy_attribute
    def end_time(self):
        if not self.start_time:
            return None
        return self.start_time + timedelta(hours=1)


class MeetingFactory(AppointmentFactory):
    """Especialização para Reuniões."""

    event_type = Appointment.EventType.MEETING
    title = factory.Sequence(lambda n: f"Reunião de Alinhamento {n}")


class TaskFactory(factory.django.DjangoModelFactory):
    """Fábrica para Tarefas do Checklist."""

    class Meta:
        model = Task

    event = factory.SubFactory(EventFactory)
    company = factory.SelfAttribute("event.company")

    title = factory.Faker("sentence", nb_words=3)
    due_date = factory.Faker("future_date")
    is_completed = False
