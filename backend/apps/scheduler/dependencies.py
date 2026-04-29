from uuid import UUID

from django.http import HttpRequest

from apps.scheduler.models import Appointment, Task


def get_appointment(request: HttpRequest, uuid: UUID) -> Appointment:
    """Injeta a instância de Appointment (Agenda) validada para o usuário logado."""
    return Appointment.objects.resolve(request.user, uuid)


def get_task(request: HttpRequest, uuid: UUID) -> Task:
    """Injeta a instância de Task validada para o usuário logado."""
    return Task.objects.resolve(request.user, uuid)
