"""
ViewSets para a API REST de Item.
"""

import logging

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.items.models import Item

from .permissions import IsItemOwner
from .serializers import ItemDetailSerializer, ItemListSerializer, ItemSerializer

logger = logging.getLogger(__name__)


class ItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operações CRUD de Item via API REST.
    Endpoints disponíveis:
    - GET    /api/v1/items/          - Lista itens do usuário
    - POST   /api/v1/items/          - Cria novo item
    - GET    /api/v1/items/{id}/     - Detalhes do item
    - PUT    /api/v1/items/{id}/     - Atualiza item completo
    - PATCH  /api/v1/items/{id}/     - Atualiza parcialmente
    - DELETE /api/v1/items/{id}/     - Deleta item
    - PATCH  /api/v1/items/{id}/update_status/ - Atualiza status

    Permissões:
    - Requer autenticação (IsAuthenticated)
    - Apenas o planner dono do wedding pode acessar (IsItemOwner)

    Serializers:
    - Lista: ItemListSerializer (campos otimizados)
    - Detalhe: ItemDetailSerializer (campos completos)
    - Create/Update: ItemSerializer (campos editáveis)
    """

    permission_classes = [IsAuthenticated, IsItemOwner]

    def get_queryset(self):
        """
        Retorna apenas os itens dos weddings do usuário logado.

        Aplica filtros, ordenação e anotações do ItemQuerySet.
        """
        queryset = Item.objects.filter(
            wedding__planner=self.request.user
        )

        # Suporta filtros via query params
        wedding_id = self.request.query_params.get('wedding', None)
        if wedding_id:
            queryset = queryset.filter(wedding_id=wedding_id)

        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)

        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        search = self.request.query_params.get('q', None)
        if search:
            queryset = queryset.filter(name__icontains=search)

        # Ordenação
        sort = self.request.query_params.get('sort', '-created_at')
        queryset = queryset.order_by(sort)

        # Select related para otimização
        queryset = queryset.select_related('wedding')

        return queryset

    def get_serializer_class(self):
        """
        Retorna o serializer apropriado baseado na action.

        - list: ItemListSerializer (otimizado)
        - retrieve: ItemDetailSerializer (completo)
        - create/update/partial_update: ItemSerializer (editável)
        """
        if self.action == 'list':
            return ItemListSerializer
        elif self.action == 'retrieve':
            return ItemDetailSerializer
        return ItemSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        """
        Cria o item com transaction.atomic() para garantir integridade.

        CRITICAL: Se a criação do contrato falhar, o item é revertido.
        """
        item = serializer.save()

        # Criar contrato automaticamente (se houver lógica)
        # Contract.objects.create(item=item) - Exemplo

        logger.info(
            f"Item criado via API: '{item.name}' "
            f"(ID: {item.id}) para wedding {item.wedding_id} "
            f"pelo usuário {self.request.user.id}"
        )

    def perform_update(self, serializer):
        """
        Loga a atualização do item.
        """
        item = serializer.save()
        logger.info(
            f"Item {item.id} atualizado via API "
            f"pelo usuário {self.request.user.id}"
        )

    def perform_destroy(self, instance):
        """
        Loga a exclusão do item antes de deletar.
        """
        item_repr = str(instance)
        item_id = instance.id
        instance.delete()
        logger.info(
            f"Item DELETADO via API: '{item_repr}' "
            f"(ID: {item_id}) pelo usuário {self.request.user.id}"
        )

    @action(
        detail=True,
        methods=['patch'],
        url_path='update-status',
        url_name='update_status'
    )
    def update_status(self, request, pk=None):
        """
        Endpoint customizado para atualizar apenas o status.

        PATCH /api/v1/items/{id}/update-status/
        Body: {"status": "DONE"}

        Valida se o status é válido usando choices.
        """
        item = self.get_object()
        new_status = request.data.get('status')

        # Valida se o status é válido
        valid_statuses = [choice[0] for choice in Item.STATUS_CHOICES]
        if new_status not in valid_statuses:
            logger.warning(
                f"Status inválido recebido via API: '{new_status}'"
            )
            return Response(
                {
                    "error": f"Status '{new_status}' não é válido.",
                    "valid_statuses": valid_statuses
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        old_status = item.status
        item.status = new_status
        item.save()

        logger.info(
            f"Status do item {item.id} alterado via API de "
            f"'{old_status}' para '{new_status}' "
            f"pelo usuário {request.user.id}"
        )

        serializer = self.get_serializer(item)
        return Response(serializer.data)
