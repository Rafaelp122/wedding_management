"""
Fábricas do Agendamento (Scheduler Factories).

Este ficheiro define os blueprints para Eventos de calendário.
Essencial para testar a agenda do planner e lembretes automáticos.

Destaques Técnicos:
- Integridade de Tenant: Garante que o Planner do evento seja o mesmo do Casamento.
- Lógica de Datas: Usa LazyAttribute para garantir que o fim do evento seja após o
início.
- Variedade de Tipos: Utiliza Iterator para cobrir os diferentes TypeChoices do modelo.
"""

from datetime import timedelta

import factory
from django.utils import timezone

from apps.scheduler.models import Event
from apps.weddings.tests.model_factories import WeddingFactory


class EventFactory(factory.django.DjangoModelFactory):
    """Fábrica para Eventos de Calendário."""

    class Meta:
        model = Event

    # Garante que o planner do evento seja o dono do casamento vinculado
    wedding = factory.SubFactory(WeddingFactory)
    planner = factory.SelfAttribute("..wedding.planner")

    title = factory.Faker("sentence", nb_words=4)
    location = factory.Faker("address")
    description = factory.Faker("paragraph")

    event_type = factory.Iterator([
        Event.TypeChoices.MEETING,
        Event.TypeChoices.VISIT,
        Event.TypeChoices.TASTING,
        Event.TypeChoices.OTHER,
    ])

    # Datas e Horários
    start_time = factory.Faker(
        "future_datetime", tzinfo=timezone.get_current_timezone()
    )

    @factory.lazy_attribute
    def end_time(self):
        """Define o fim do evento como 1 hora após o início por padrão."""
        if not self.start_time:
            return None
        return self.start_time + timedelta(hours=1)

    # Configurações de Lembrete (RF12)
    reminder_enabled = factory.Faker("boolean")
    reminder_minutes_before = 60


class MeetingFactory(EventFactory):
    """Especialização para Reuniões."""

    event_type = Event.TypeChoices.MEETING
    title = factory.Sequence(lambda n: f"Reunião de Alinhamento {n}")
