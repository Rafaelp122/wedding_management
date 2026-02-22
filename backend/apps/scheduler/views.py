from drf_spectacular.utils import extend_schema

from apps.core.viewsets import BaseViewSet
from apps.scheduler.models import Event
from apps.scheduler.serializers import EventSerializer
from apps.scheduler.services import EventService


@extend_schema(tags=["Scheduler"])
class EventsViewSet(BaseViewSet):
    """
    Gestão de eventos e compromissos do calendário.

    Este endpoint centraliza a organização da agenda do Planner, permitindo o
    controle de reuniões, visitas técnicas, degustações e prazos de pagamento (RF12).

    A arquitetura garante que lembretes e validações de horário sejam processados
    antes da persistência.
    """

    # Otimização: select_related evita múltiplas consultas ao banco para obter
    # os dados do casamento e do planner vinculados ao evento.
    queryset = Event.objects.select_related("wedding", "planner").all()
    serializer_class = EventSerializer
    service_class = EventService
