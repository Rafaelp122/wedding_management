from uuid import UUID

from django.http import HttpRequest

from apps.events.models import Event


def get_event(request: HttpRequest, uuid: UUID) -> Event:
    """Injeta a instância de Event validada para o usuário logado."""
    return Event.objects.resolve(request.user, uuid)
