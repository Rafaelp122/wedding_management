"""
Views da API de Events (Scheduler).
"""
import logging

from django.db import transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.scheduler.models import Event

from .permissions import IsEventOwner
from .serializers import (EventDetailSerializer, EventListSerializer,
                          EventSerializer)

logger = logging.getLogger(__name__)


class EventViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento completo de eventos via API REST.

    Endpoints disponíveis:
    - GET /api/v1/scheduler/events/ - Lista eventos (filtros disponíveis)
    - POST /api/v1/scheduler/events/ - Cria novo evento
    - GET /api/v1/scheduler/events/{id}/ - Detalhes de um evento
    - PUT /api/v1/scheduler/events/{id}/ - Atualiza evento completo
    - PATCH /api/v1/scheduler/events/{id}/ - Atualiza evento parcial
    - DELETE /api/v1/scheduler/events/{id}/ - Remove evento
    - POST /api/v1/scheduler/events/{id}/mark-as-done/ - Marca como concluído

    Filtros disponíveis (query params):
    - wedding: Filtra por ID do casamento
    - category: Filtra por categoria (MEETING, TASK, APPOINTMENT, etc.)
    - priority: Filtra por prioridade (LOW, MEDIUM, HIGH)
    - start_date: Filtra eventos a partir desta data
    - end_date: Filtra eventos até esta data
    - is_past: true/false - eventos passados ou futuros
    - q: Busca por título ou descrição
    """

    queryset = Event.objects.all()
    permission_classes = [IsEventOwner]

    def get_queryset(self):
        """
        Retorna apenas eventos dos casamentos do planner autenticado.
        Aplica filtros opcionais via query params.
        """
        queryset = Event.objects.for_planner(self.request.user)

        # Filtro por casamento
        wedding_id = self.request.query_params.get('wedding')
        if wedding_id:
            queryset = queryset.filter(wedding_id=wedding_id)

        # Filtro por categoria
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Filtro por prioridade
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filtro por range de datas
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.in_range(start_date, end_date)
        elif start_date:
            queryset = queryset.filter(start__gte=start_date)
        elif end_date:
            queryset = queryset.filter(end__lte=end_date)

        # Filtro por eventos passados/futuros
        is_past = self.request.query_params.get('is_past')
        if is_past is not None:
            now = timezone.now()
            if is_past.lower() == 'true':
                queryset = queryset.filter(end__lt=now)
            elif is_past.lower() == 'false':
                queryset = queryset.filter(end__gte=now)

        # Busca textual
        search_query = self.request.query_params.get('q')
        if search_query:
            queryset = queryset.search(search_query)

        # Ordenação (padrão: por data de início)
        sort = self.request.query_params.get('sort', 'start')
        if sort == 'priority':
            queryset = queryset.order_by('-priority', 'start')
        elif sort == '-priority':
            queryset = queryset.order_by('priority', 'start')
        elif sort == '-start':
            queryset = queryset.order_by('-start')
        else:
            queryset = queryset.order_by('start')

        return queryset.select_related('wedding')

    def get_serializer_class(self):
        """Retorna o serializer apropriado para cada ação."""
        if self.action == 'list':
            return EventListSerializer
        elif self.action == 'retrieve':
            return EventDetailSerializer
        return EventSerializer

    def create(self, request, *args, **kwargs):
        """Cria um novo evento."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            event = serializer.save()
            logger.info(
                f"[API] Evento '{event.title}' (ID: {event.id}) "
                f"criado para o casamento {event.wedding_id} "
                f"pelo usuário {request.user.id}"
            )

        # Retorna com serializer detalhado
        output_serializer = EventDetailSerializer(event)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )

    def update(self, request, *args, **kwargs):
        """Atualiza um evento (PUT ou PATCH)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            event = serializer.save()
            logger.info(
                f"[API] Evento '{event.title}' (ID: {event.id}) "
                f"atualizado pelo usuário {request.user.id}"
            )

        # Retorna com serializer detalhado
        output_serializer = EventDetailSerializer(event)
        return Response(output_serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Remove um evento."""
        instance = self.get_object()
        event_id = instance.id
        event_title = instance.title

        with transaction.atomic():
            self.perform_destroy(instance)
            logger.info(
                f"[API] Evento '{event_title}' (ID: {event_id}) "
                f"deletado pelo usuário {request.user.id}"
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def mark_as_done(self, request, pk=None):
        """
        Marca um evento como concluído alterando a prioridade para LOW.

        Endpoint: POST /api/v1/scheduler/events/{id}/mark-as-done/
        """
        event = self.get_object()

        with transaction.atomic():
            event.priority = 'LOW'
            event.save(update_fields=['priority'])
            logger.info(
                f"[API] Evento '{event.title}' (ID: {event.id}) "
                f"marcado como concluído pelo usuário {request.user.id}"
            )

        serializer = EventDetailSerializer(event)
        return Response(serializer.data)
