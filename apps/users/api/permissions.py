"""
Permissions customizadas para a API de Users.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permission que permite:
    - Leitura para qualquer usuário autenticado
    - Escrita apenas para o dono do perfil

    Usado em:
    - Retrieve, Update, Delete de perfis de usuário
    """

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário pode acessar/editar o perfil.

        Args:
            request: Request object
            view: View sendo acessada
            obj: Objeto User sendo acessado

        Returns:
            bool: True se é método safe ou se é o próprio usuário
        """
        # Métodos SAFE (GET, HEAD, OPTIONS) permitidos para todos
        if request.method in permissions.SAFE_METHODS:
            return True

        # Métodos de escrita (PUT, PATCH, DELETE) apenas para o dono
        return obj == request.user


class IsSelfOrAdmin(permissions.BasePermission):
    """
    Permission que permite acesso apenas ao próprio usuário ou admin.

    Mais restritiva que IsOwnerOrReadOnly - não permite leitura de
    outros perfis.

    Usado em:
    - Endpoints sensíveis como troca de senha
    """

    def has_object_permission(self, request, view, obj):
        """
        Verifica se é o próprio usuário ou admin.

        Args:
            request: Request object
            view: View sendo acessada
            obj: Objeto User sendo acessado

        Returns:
            bool: True se é o próprio usuário ou staff
        """
        return obj == request.user or request.user.is_staff
