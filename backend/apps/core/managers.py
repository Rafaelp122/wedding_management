"""
Managers e QuerySets customizados para o sistema.
"""

from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    """QuerySet personalizado para soft delete."""

    def delete(self):
        """Soft delete em lote."""
        return super().update(is_deleted=True, deleted_at=timezone.now())

    def hard_delete(self):
        """Delete permanente. USE COM CUIDADO."""
        return super().delete()

    def restore(self):
        """Restaura registros soft deleted."""
        return super().update(is_deleted=False, deleted_at=None)


class SoftDeleteManager(models.Manager):
    """Manager que filtra automaticamente registros ativos."""

    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=False)

    def deleted(self):
        """Retorna apenas registros deletados (lixeira)."""
        return SoftDeleteQuerySet(self.model, using=self._db).filter(is_deleted=True)
