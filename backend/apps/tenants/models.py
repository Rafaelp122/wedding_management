from django.db import models

from apps.core.models import BaseModel


class Company(BaseModel):
    """
    Entidade central de Multitenancy (ADR-009 / ADR-016).
    Representa a 'Empresa' ou 'Agência' do Organizador.
    """

    name = models.CharField("Nome da Empresa", max_length=255)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.name
