"""
Fábricas do Agendamento (Scheduler Factories).
"""

from datetime import timedelta

import factory
from django.utils import timezone

from apps.scheduler.models import Event, Task
from apps.weddings.tests.factories import WeddingFactory


class EventFactory(factory.django.DjangoModelFactory):
    """Fábrica para Eventos de Calendário."""

    class Meta:
        model = Event

    wedding = factory.SubFactory(WeddingFactory)
    # Planner vem do casamento vinculado
    planner = factory.SelfAttribute("wedding.planner")

    title = factory.Faker("sentence", nb_words=4)
    location = factory.Faker("address")
    description = factory.Faker("paragraph")

    event_type = factory.Iterator(
        [
            Event.TypeChoices.MEETING,
            Event.TypeChoices.VISIT,
            Event.TypeChoices.TASTING,
            Event.TypeChoices.OTHER,
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

    reminder_enabled = factory.Faker("boolean")
    reminder_minutes_before = 60


class MeetingFactory(EventFactory):
    """Especialização para Reuniões."""

    event_type = Event.TypeChoices.MEETING
    title = factory.Sequence(lambda n: f"Reunião de Alinhamento {n}")


class TaskFactory(factory.django.DjangoModelFactory):
    """Fábrica para Tarefas do Checklist."""

    class Meta:
        model = Task

    wedding = factory.SubFactory(WeddingFactory)
    planner = factory.SelfAttribute("wedding.planner")

    title = factory.Faker("sentence", nb_words=3)
    due_date = factory.Faker("future_date")
    is_completed = False
