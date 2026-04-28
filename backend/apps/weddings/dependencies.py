from uuid import UUID

from django.http import HttpRequest

from apps.weddings.models import Wedding


def get_wedding(request: HttpRequest, uuid: UUID) -> Wedding:
    """Injeta a instância de Wedding validada para o usuário logado."""
    return Wedding.objects.resolve(request.user, uuid)
