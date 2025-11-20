"""
Views JSON simples para o Scheduler.

Substituição do DRF por views Django nativas para reduzir dependências.
"""

import logging

from django.http import JsonResponse
from django.views import View

from apps.core.mixins.auth import LoginRequiredMixin

from .models import Event

logger = logging.getLogger(__name__)


class EventsJsonView(LoginRequiredMixin, View):
    """
    Retorna eventos em formato JSON para o FullCalendar.

    Esta view substitui o EventViewSet do DRF, eliminando a
    dependência do Django Rest Framework para uma simples
    listagem de eventos.

    Query Parameters:
        wedding_id (int): ID do casamento para filtrar eventos.

    Returns:
        JSON array com eventos no formato FullCalendar:
        [{
            id: int,
            title: str,
            start: ISO datetime string,
            end: ISO datetime string | null,
            description: str,
            event_type: str,
            location: str
        }]

    Security:
        - Requer autenticação (LoginRequiredMixin)
        - Filtra apenas eventos do planner logado
        - Opcionalmente filtra por wedding_id
    """

    def get(self, request):
        """
        GET handler que retorna eventos do usuário em JSON.

        Args:
            request: HttpRequest com query params opcionais.

        Returns:
            JsonResponse com array de eventos.
        """
        # Filtra eventos do usuário logado usando QuerySet customizado
        queryset = Event.objects.for_planner(request.user)

        # Filtra por casamento se fornecido
        wedding_id = request.GET.get("wedding_id")
        if wedding_id:
            queryset = queryset.for_wedding_id(wedding_id)
            logger.info(
                f"Events API called: wedding_id={wedding_id}, "
                f"user={request.user.username}, "
                f"count={queryset.count()}"
            )
        else:
            logger.info(
                f"Events API called: all weddings, "
                f"user={request.user.username}, "
                f"count={queryset.count()}"
            )

        # Serializa manualmente para o formato FullCalendar
        events = [
            {
                "id": event.id,
                "title": event.title,
                "start": event.start_time.isoformat(),
                "end": event.end_time.isoformat() if event.end_time else None,
                "description": event.description or "",
                "event_type": event.event_type,
                "location": event.location or "",
            }
            for event in queryset
        ]

        return JsonResponse(events, safe=False)
