"""
ViewSets para a API REST de Wedding.
"""

import logging
from typing import ClassVar

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.weddings.models import Wedding

from .permissions import IsWeddingOwner
from .serializers import (
    WeddingDetailSerializer,
    WeddingListSerializer,
    WeddingSerializer,
)

logger = logging.getLogger(__name__)


class WeddingViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Wedding via API REST.

    Endpoints disponíveis:
    - GET    /api/v1/weddings/          - Lista casamentos do usuário
    - POST   /api/v1/weddings/          - Cria novo casamento
    - GET    /api/v1/weddings/{id}/     - Detalhes do casamento
    - PUT    /api/v1/weddings/{id}/     - Atualiza casamento completo
    - PATCH  /api/v1/weddings/{id}/     - Atualiza parcialmente
    - DELETE /api/v1/weddings/{id}/     - Deleta casamento
    - PATCH  /api/v1/weddings/{id}/update_status/ - Atualiza status

    Permissões:
    - Requer autenticação (IsAuthenticated)
    - Apenas o planner dono pode acessar seus casamentos (IsWeddingOwner)

    Serializers:
    - Lista: WeddingListSerializer (campos otimizados)
    - Detalhe: WeddingDetailSerializer (campos completos)
    - Create/Update: WeddingSerializer (campos editáveis)
    """

    permission_classes: ClassVar[list] = [IsAuthenticated, IsWeddingOwner]

    def get_queryset(self):
        """
        Retorna apenas os casamentos do usuário logado.

        Aplica filtros, ordenação e anotações do WeddingQuerySet.
        """
        queryset = Wedding.objects.filter(planner=self.request.user)
        queryset = queryset.with_effective_status()
        queryset = queryset.with_counts_and_progress()

        # Suporta filtros via query params
        status_filter = self.request.query_params.get("status", None)
        if status_filter:
            queryset = queryset.filter(effective_status=status_filter)

        search = self.request.query_params.get("q", None)
        if search:
            queryset = queryset.apply_search(search)

        sort = self.request.query_params.get("sort", "id")
        queryset = queryset.apply_sort(sort)

        return queryset

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na action.

        - list: WeddingListSerializer (otimizado)
        - retrieve: WeddingDetailSerializer (completo)
        - create/update/partial_update: WeddingSerializer (editável)
        """
        if self.action == "list":
            return WeddingListSerializer
        elif self.action == "retrieve":
            return WeddingDetailSerializer
        return WeddingSerializer

    def perform_create(self, serializer):
        """
        Define o planner do casamento como o usuário logado.
        """
        wedding = serializer.save(planner=self.request.user)
        logger.info(
            f"Casamento criado via API: '{wedding}' "
            f"(ID: {wedding.id}) pelo usuário {self.request.user.id}"
        )

    def perform_update(self, serializer):
        """
        Loga a atualização do casamento.
        """
        wedding = serializer.save()
        logger.info(
            f"Casamento {wedding.id} atualizado via API "
            f"pelo usuário {self.request.user.id}"
        )

    def perform_destroy(self, instance):
        """
        Loga a exclusão do casamento antes de deletar.
        """
        wedding_repr = str(instance)
        wedding_id = instance.id
        instance.delete()
        logger.info(
            f"Casamento DELETADO via API: '{wedding_repr}' "
            f"(ID: {wedding_id}) pelo usuário {self.request.user.id}"
        )

    @action(
        detail=True,
        methods=["patch"],
        url_path="update-status",
        url_name="update_status",
    )
    def update_status(self, request, pk=None):
        """
        Endpoint customizado para atualizar apenas o status.

        PATCH /api/v1/weddings/{id}/update-status/
        Body: {"status": "COMPLETED"}

        Valida se o status é válido usando TextChoices.
        """
        wedding = self.get_object()
        new_status = request.data.get("status")

        # Valida se o status é válido
        try:
            Wedding.StatusChoices(new_status)
        except ValueError:
            logger.warning(f"Status inválido recebido via API: '{new_status}'")
            return Response(
                {
                    "error": f"Status '{new_status}' não é válido.",
                    "valid_statuses": [
                        choice[0] for choice in Wedding.StatusChoices.choices
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        old_status = wedding.status
        wedding.status = new_status
        wedding.save()

        logger.info(
            f"Status do casamento {wedding.id} alterado via API de "
            f"'{old_status}' para '{new_status}' "
            f"pelo usuário {request.user.id}"
        )

        serializer = self.get_serializer(wedding)
        return Response(serializer.data)
