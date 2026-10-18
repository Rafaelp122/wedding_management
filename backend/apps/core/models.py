from typing import Any, Self, cast
from uuid import UUID, uuid4

from django.db import models


class BaseModel(models.Model):
    """
    Modelo base abstrato para todas as entidades do sistema.

    Decisão Arquitetural:
        ADR-007 (docs/architecture/adr/007-hybrid-keys.md)
    """

    id = models.BigAutoField(primary_key=True, editable=False)
    uuid = models.UUIDField(default=uuid4, unique=True, editable=False, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def save(self, *args: Any, skip_clean: bool = False, **kwargs: Any) -> None:
        """
        Executa validações intrínsecas via full_clean antes de persistir o registro.

        Decisão Arquitetural:
            ADR-011 (docs/architecture/adr/011-basemodel-save-full-clean.md)

        Args:
            skip_clean: Se True, ignora o full_clean(). Uso restrito a migrações
                e operações em lote de alta performance.
        """
        if not skip_clean:
            self.full_clean()
        super().save(*args, **kwargs)

    @classmethod
    def get_by_uuid(cls, uuid_value: UUID | str) -> Self | None:
        """
        Busca rápida de registro pelo seu identificador público UUID.

        Returns:
            Instância encontrada ou None se inexistente.
        """
        return cast(Self | None, cls.objects.filter(uuid=uuid_value).first())  # type: ignore[attr-defined]
