from django.db import models

from apps.core.models import BaseModel
from apps.tenants.managers import TenantManager


class Company(BaseModel):
    """
    Representa o Tenant (Empresa) do sistema.

    Isola os dados operacionais de assessorias, cerimonias ou casais.
    """

    name = models.CharField("Nome da Empresa", max_length=255)
    is_active = models.BooleanField("Ativa", default=True)
    slug = models.SlugField(unique=True, help_text="Identificador único na URL")

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["name"]
        db_table = "companies"

    def clean(self) -> None:
        """Sanitiza o slug para garantir consistência em URLs e rotas."""
        super().clean()
        if self.slug:
            self.slug = self.slug.strip().lower()

    def __str__(self) -> str:
        return self.name


class TenantModel(BaseModel):
    """
    Modelo base abstrato para entidades vinculadas a um Tenant.

    Garante isolamento automático de dados via Company e aplicação do TenantManager.
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
