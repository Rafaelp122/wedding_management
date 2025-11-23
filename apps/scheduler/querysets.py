"""
QuerySets customizados para o app scheduler.

Este módulo fornece QuerySets com métodos auxiliares para
facilitar consultas comuns no modelo Event.
"""
from django.db import models


class EventQuerySet(models.QuerySet):
    """
    QuerySet customizado para o modelo Event.

    Fornece métodos auxiliares para filtros e consultas comuns,
    melhorando a legibilidade e reusabilidade do código.
    """

    def for_planner(self, user):
        """
        Filtra eventos de um planner específico.

        Args:
            user: Instância do User (planner).

        Returns:
            QuerySet filtrado com eventos do planner.
        """
        return self.filter(planner=user)

    def for_wedding_id(self, wedding_id):
        """
        Filtra eventos de um casamento específico por ID.

        Args:
            wedding_id: ID do Wedding.

        Returns:
            QuerySet filtrado com eventos do casamento.
        """
        return self.filter(wedding_id=wedding_id)
