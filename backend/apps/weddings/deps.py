from django.http import HttpRequest
from pydantic import UUID4

from apps.weddings.services import WeddingService


def get_current_wedding(request: HttpRequest, uuid: UUID4):
    """
    Dependência para buscar e validar o casamento atual.
    """
    # O método .get já lança ObjectNotFoundError (ou 404) se não existir
    return WeddingService.get(user=request.user, uuid=uuid)
