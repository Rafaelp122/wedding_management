from typing import Any, Self
from uuid import UUID, uuid4

from django.db import models

from .managers import BaseManager


class BaseModel(models.Model):
    """
    Model base para todos os modelos do sistema (ADR-007).
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BaseManager()

    class Meta:
        abstract = True

    def save(self, *args: Any, skip_clean: bool = False, **kwargs: Any) -> None:
        """Garante a execução das validações do clean() antes de persistir (ADR-011).

        Args:
            skip_clean: Se True, pula o full_clean(). Usar apenas em cenários
                controlados como bulk operations, migrations ou fixtures onde a
                validação já foi feita externamente.
        """
        if not skip_clean:
            self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_by_uuid(cls, uuid_value: UUID | str) -> Self | None:
        """Busca rápida por identificador público."""
        return cls.objects.filter(uuid=uuid_value).first()
