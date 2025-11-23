"""
Permissões customizadas para a API de Wedding.
"""

from rest_framework import permissions


class IsWeddingOwner(permissions.BasePermission):
    """
    Permissão para garantir que apenas o planner dono do wedding
    pode visualizar, editar ou deletar.

    Usage:
        class WeddingViewSet(ModelViewSet):
            permission_classes = [IsAuthenticated, IsWeddingOwner]
    """

    message = "Você não tem permissão para acessar este casamento."

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário é o planner do casamento.

        Args:
            request: HttpRequest object
            view: APIView instance
            obj: Wedding instance

        Returns:
            bool: True se o usuário é o planner, False caso contrário
        """
        # Garante que o casamento pertence ao usuário logado
        return obj.planner == request.user
