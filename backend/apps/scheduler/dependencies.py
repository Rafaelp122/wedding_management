from uuid import UUID

from django.http import HttpRequest

from apps.scheduler.models import Event, Task


def get_event(request: HttpRequest, uuid: UUID) -> Event:
    """Injeta a instância de Event (Agenda) validada para o usuário logado."""
    return Event.objects.resolve(request.user, uuid)


def get_task(request: HttpRequest, uuid: UUID) -> Task:
    """Injeta a instância de Task validada para o usuário logado."""
    return Task.objects.resolve(request.user, uuid)
