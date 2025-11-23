"""
Permissões customizadas para a API de Item.
"""

from rest_framework import permissions


class IsItemOwner(permissions.BasePermission):
    """
    Permissão para garantir que apenas o planner dono do wedding
    pode visualizar, editar ou deletar itens.
    
    Usage:
        class ItemViewSet(ModelViewSet):
            permission_classes = [IsAuthenticated, IsItemOwner]
    """
    
    message = "Você não tem permissão para acessar este item."
    
    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário é o planner do wedding do item.
        
        Args:
            request: HttpRequest object
            view: APIView instance
            obj: Item instance
        
        Returns:
            bool: True se o usuário é o planner, False caso contrário
        """
        # Garante que o item pertence a um wedding do usuário logado
        return obj.wedding and obj.wedding.planner == request.user
