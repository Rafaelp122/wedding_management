from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.decorators import action

from .models import Event
from .serializers import EventSerializer


class IsPlannerOwner(permissions.BasePermission):
    """Permissão personalizada: apenas o planner dono do evento pode acessar/modificar."""

    def has_object_permission(self, request, view, obj):
        return obj.planner == request.user

    def has_permission(self, request, view):
        return request.user.is_authenticated


class EventViewSet(viewsets.ModelViewSet):
    """ViewSet DRF para CRUD de eventos, filtrados pelo planner logado."""

    serializer_class = EventSerializer
    permission_classes = [IsPlannerOwner]

    def get_queryset(self):
        """Retorna apenas os eventos do planner logado (ou de um casamento específico)."""
        user = self.request.user
        wedding_id = self.request.query_params.get("wedding_id")

        queryset = Event.objects.filter(planner=user)
        if wedding_id:
            queryset = queryset.filter(wedding_id=wedding_id)

        return queryset

    def perform_create(self, serializer):
        """Define o planner automaticamente como o usuário logado."""
        serializer.save(planner=self.request.user)

    @action(detail=False, methods=["get"])
    def my_events(self, request):
        """Endpoint extra: retorna todos os eventos do planner logado."""
        events = self.get_queryset()
        serializer = self.get_serializer(events, many=True)
        return Response(serializer.data)
