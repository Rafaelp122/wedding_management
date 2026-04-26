"""
Configuração Local de Testes: App Scheduler.
"""

import pytest
from pytest_factoryboy import register

from apps.scheduler.services.events import EventService
from apps.weddings.services import WeddingService

# Mantendo as importações relativas como solicitado
from .factories import EventFactory, MeetingFactory, TaskFactory


# Registo das factories como fixtures (ex: event_factory)
register(EventFactory)
register(MeetingFactory)
register(TaskFactory)


@pytest.fixture
def scheduler_seed(db, user, django_user_model):
    """
    Cenário completo de isolamento do cronograma (Multitenancy).
    Cria dados para o usuário autenticado e para um usuário alheio.
    """
    # Planner alvo (Meu)
    my_wedding = WeddingService.create(
        user,
        {
            "bride_name": "Minha",
            "groom_name": "Noiva",
            "location": "A",
            "date": "2026-10-11",
        },
    )
    my_event = EventService.create(
        user,
        {
            "wedding": my_wedding,
            "title": "Reunião A",
            "event_type": "reuniao",
            "start_time": "2026-10-11T10:00:00Z",
            "end_time": "2026-10-11T11:00:00Z",
        },
    )

    # Planner alheio (Outro)
    other_user = django_user_model.objects.create_user(
        email="other_scheduler@test.com", password="123"
    )
    other_wedding = WeddingService.create(
        other_user,
        {
            "bride_name": "Outra",
            "groom_name": "Outro",
            "location": "B",
            "date": "2026-10-11",
        },
    )
    other_event = EventService.create(
        other_user,
        {
            "wedding": other_wedding,
            "title": "Reunião B",
            "event_type": "reuniao",
            "start_time": "2026-10-11T12:00:00Z",
            "end_time": "2026-10-11T13:00:00Z",
        },
    )

    return {
        "my_event": my_event,
        "other_user": other_user,
        "other_event": other_event,
    }
