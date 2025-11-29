"""
Permissions customizadas para a API de Events (Scheduler).
"""

from rest_framework import permissions


class IsEventOwner(permissions.BasePermission):
    """
    Permission que permite acesso apenas ao planner dono do casamento do evento.

    Verifica se o usuário autenticado é o planner do casamento
    associado ao evento.

    Usado em:
    - Retrieve, Update, Delete de eventos individuais
    """

    def has_object_permission(self, request, view, obj):
        """
        Verifica se o usuário é o dono do evento através do casamento.

        Args:
            request: Request object
            view: View sendo acessada
            obj: Objeto Event sendo acessado

        Returns:
            bool: True se o usuário é o planner do casamento do evento
        """
        # obj é um Event, acessamos obj.wedding.planner
        if obj.wedding:
            return obj.wedding.planner == request.user

        # Se não tem wedding associado, só o criador pode acessar
        # (caso de uso improvável, mas seguro)
        return False
