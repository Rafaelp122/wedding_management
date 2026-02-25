from drf_spectacular.utils import extend_schema
from rest_framework import filters  # <-- Importe isto

from apps.core.viewsets import BaseViewSet

from .models import Wedding
from .serializers import WeddingSerializer
from .services import WeddingService


@extend_schema(tags=["Weddings"])
class WeddingViewSet(BaseViewSet):
    """
    Gestão de casamentos.

    Este endpoint centraliza a criação e controle do ciclo de vida
    dos casamentos gerenciados pelo Planner logado.
    """

    queryset = Wedding.objects.all()
    serializer_class = WeddingSerializer
    service_class = WeddingService
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["groom_name", "bride_name", "location"]
    ordering_fields = ["date", "created_at", "total_estimated"]
    ordering = ["date"]
