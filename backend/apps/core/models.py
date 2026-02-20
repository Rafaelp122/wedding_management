import uuid

from django.db import models

from .managers import BaseManager


class BaseModel(models.Model):
    """
    Model base para todos os modelos do sistema (ADR-007).
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    uuid = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    class Meta:
        abstract = True

    @classmethod
    def get_by_uuid(cls, uuid_value):
        """Busca rápida por identificador público."""
        return cls.objects.filter(uuid=uuid_value).first()
