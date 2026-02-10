"""
Models abstratos base do sistema.

DESIGN DECISION (RNF04): Soft delete implementado no MVP para prevenir perda
de dados críticos. Aplicado seletivamente em: Wedding, BudgetCategory, Item,
Contract, Supplier. Cascade manual via service layer por simplicidade.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone

from .managers import SoftDeleteManager


class BaseModel(models.Model):
    """
    Model base para todos os models do sistema.

    Fornece (RNF05):
    - ID auto-incremento (interno, performance em JOINs)
    - UUID (identificador público para APIs, segurança)
    - Timestamps automáticos (created_at, updated_at)
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    @classmethod
    def get_by_uuid(cls, uuid_value):
        """Helper para buscar por UUID público na API."""
        try:
            return cls.objects.get(uuid=uuid_value)
        except cls.DoesNotExist:
            return None


class SoftDeleteModel(BaseModel):
    """
    Model base com soft delete (RNF04).

    IMPORTANTE: Cascade NÃO é automático. Use service layer para deletar
    relacionamentos antes de deletar o modelo principal.

    Aplicado em: Wedding, BudgetCategory, Item, Contract, Supplier

    Uso:
        obj.delete()       # Soft delete (esconde do queryset padrão)
        obj.restore()      # Restaura registro
        obj.hard_delete()  # Delete permanente (não tem volta!)

        Model.objects.all()              # Apenas ativos
        Model.all_objects.all()          # Todos (inclusive deletados)
        Model.objects.deleted().all()    # Apenas deletados (lixeira)
    """

    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    all_objects = models.Manager()
    objects = SoftDeleteManager()

    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=["is_deleted", "created_at"]),
        ]

    def delete(self, using=None, keep_parents=False):
        """Soft delete."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(using=using, update_fields=["is_deleted", "deleted_at", "updated_at"])

    def hard_delete(self, using=None, keep_parents=False):
        """Delete permanente do banco de dados."""
        return super().delete(using=using, keep_parents=keep_parents)

    def restore(self, using=None):
        """Restaura um registro soft deleted."""
        self.is_deleted = False
        self.deleted_at = None
        self.save(using=using, update_fields=["is_deleted", "deleted_at", "updated_at"])


class WeddingOwnedModel(models.Model):
    """
    Mixin para garantir que o modelo pertença a um casamento específico.
    Essencial para o Multitenancy rigoroso (RF01).
    """

    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.CASCADE,
        verbose_name="Casamento",
    )

    class Meta:
        abstract = True


class UserOwnedModel(models.Model):
    """
    Mixin para modelos que pertencem ao usuário (Planner) e não a um casamento.
    Caso específico do Supplier (Fornecedor).
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="%(class)ss",
        verbose_name="Usuário Responsável",
    )

    class Meta:
        abstract = True
