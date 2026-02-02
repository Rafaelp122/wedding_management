import uuid6
from django.db import models


class BaseModel(models.Model):
    """
    Modelo abstrato base para todos os modelos do sistema.

    Características:
    - ID primário usando UUID7 (ordenado por tempo)
    - Timestamps automáticos (created_at, updated_at)
    - Performance superior ao auto-increment em bancos distribuídos
    """

    # UUID7 combina timestamp + aleatoriedade = ordenação natural + unicidade
    id = models.UUIDField(primary_key=True, default=uuid6.uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        abstract = True
        ordering = ["-created_at"]
