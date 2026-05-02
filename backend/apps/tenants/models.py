from django.db import models

from apps.core.models import BaseModel
from apps.tenants.managers import TenantManager


class Company(BaseModel):
    """
    Representa o Tenant (Empresa) do sistema.
    A empresa de cerimonial, assessoria ou o próprio casal em modo self-service.
    """

    name = models.CharField("Nome da Empresa", max_length=255)
    is_active = models.BooleanField("Ativa", default=True)
    slug = models.SlugField(unique=True, help_text="Identificador único na URL")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["name"]
        db_table = "companies"

    def __str__(self) -> str:
        return self.name


class TenantModel(BaseModel):
    """
    Classe base abstrata para todos os modelos que pertencem a um Tenant.
    Garante isolamento automático de dados.
    """

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="%(class)s_records",
        verbose_name="Empresa",
    )

    objects = TenantManager()

    class Meta:
        abstract = True
        indexes = [
            # Índice composto para otimizar buscas por tenant (para performance)
            models.Index(fields=["company", "uuid"]),
        ]
