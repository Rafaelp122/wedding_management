from drf_spectacular.utils import extend_schema

from apps.core.viewsets import BaseViewSet

from .dto import WeddingDTO
from .models import Wedding
from .serializers import WeddingSerializer
from .services import WeddingService


@extend_schema(tags=["Weddings"])
class WeddingViewSet(BaseViewSet):
    """
    Gestão de casamentos utilizando arquitetura de Service/DTO.

    Este endpoint centraliza a criação e controle do ciclo de vida
    dos casamentos gerenciados pelo Planner logado.
    """

    queryset = Wedding.objects.all()
    serializer_class = WeddingSerializer
    service_class = WeddingService
    dto_class = WeddingDTO
