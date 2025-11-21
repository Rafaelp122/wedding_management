"""
Views da API de Users.
"""
import logging

from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.users.models import User

from .permissions import IsOwnerOrReadOnly, IsSelfOrAdmin
from .serializers import (
    ChangePasswordSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserSerializer,
)

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gerenciamento de usuários via API REST.
    
    Endpoints disponíveis:
    - GET /api/v1/users/ - Lista usuários
    - POST /api/v1/users/ - Registro (público)
    - GET /api/v1/users/{id}/ - Detalhes de usuário
    - PUT /api/v1/users/{id}/ - Atualiza usuário completo
    - PATCH /api/v1/users/{id}/ - Atualiza usuário parcial
    - DELETE /api/v1/users/{id}/ - Remove usuário (apenas próprio ou admin)
    - GET /api/v1/users/me/ - Perfil do usuário autenticado
    - POST /api/v1/users/{id}/change-password/ - Trocar senha
    
    Permissions:
    - POST (create): AllowAny - registro público
    - GET (list/retrieve): IsAuthenticated
    - PUT/PATCH/DELETE: IsOwnerOrReadOnly
    - change-password: IsSelfOrAdmin
    """
    
    queryset = User.objects.filter(is_active=True)
    
    def get_permissions(self):
        """Define permissões por ação."""
        if self.action == 'create':
            # Registro público
            permission_classes = [AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            # Apenas dono ou admin
            permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
        elif self.action == 'change_password':
            # Apenas próprio usuário ou admin
            permission_classes = [IsAuthenticated, IsSelfOrAdmin]
        else:
            # List, retrieve, me
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Retorna o serializer apropriado para cada ação."""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'retrieve' or self.action == 'me':
            return UserDetailSerializer
        elif self.action == 'change_password':
            return ChangePasswordSerializer
        return UserSerializer
    
    def get_queryset(self):
        """
        Retorna queryset filtrado.
        Admins veem todos, usuários normais veem apenas ativos.
        """
        queryset = User.objects.filter(is_active=True)
        
        # Filtro por busca
        search = self.request.query_params.get('q')
        if search:
            queryset = queryset.filter(
                username__icontains=search
            ) | queryset.filter(
                email__icontains=search
            ) | queryset.filter(
                first_name__icontains=search
            ) | queryset.filter(
                last_name__icontains=search
            )
        
        # Ordenação
        sort = self.request.query_params.get('sort', 'username')
        if sort in ['username', '-username', 'email', '-email', 'date_joined', '-date_joined']:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('username')
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """Cria novo usuário (registro público)."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            logger.info(
                f"[API] Novo usuário registrado: {user.username} "
                f"(ID: {user.id}, Email: {user.email})"
            )
        
        # Retorna com serializer detalhado
        output_serializer = UserDetailSerializer(user)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    def update(self, request, *args, **kwargs):
        """Atualiza usuário (PUT ou PATCH)."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        
        with transaction.atomic():
            user = serializer.save()
            logger.info(
                f"[API] Usuário {user.username} (ID: {user.id}) "
                f"atualizado por {request.user.id}"
            )
        
        # Retorna com serializer detalhado
        output_serializer = UserDetailSerializer(user)
        return Response(output_serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        'Remove' usuário (soft delete - marca como inativo).
        """
        instance = self.get_object()
        user_id = instance.id
        username = instance.username
        
        with transaction.atomic():
            instance.is_active = False
            instance.save(update_fields=['is_active'])
            logger.info(
                f"[API] Usuário {username} (ID: {user_id}) "
                f"desativado por {request.user.id}"
            )
        
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retorna perfil do usuário autenticado.
        
        Endpoint: GET /api/v1/users/me/
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Troca senha do usuário.
        
        Endpoint: POST /api/v1/users/{id}/change-password/
        Body: {"old_password": "...", "new_password": "...", "new_password2": "..."}
        """
        user = self.get_object()
        serializer = ChangePasswordSerializer(data=request.data)
        
        if serializer.is_valid():
            # Verifica senha antiga
            if not user.check_password(serializer.data.get('old_password')):
                return Response(
                    {"old_password": "Senha incorreta."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Atualiza senha
            with transaction.atomic():
                user.set_password(serializer.data.get('new_password'))
                user.save()
                logger.info(
                    f"[API] Senha alterada para usuário {user.username} "
                    f"(ID: {user.id})"
                )
            
            return Response(
                {"message": "Senha alterada com sucesso."},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
