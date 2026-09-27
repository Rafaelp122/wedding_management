"""Modelo de Fornecedores do domínio de Fornecedores (apps.suppliers).

Responsabilidade: Catálogo compartilhado de fornecedores de produtos e
serviços para casamentos, reutilizável entre contratos e itens de logística do tenant.

Referência: RF09
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
)
from django.db import models

from apps.suppliers.managers import SupplierManager
from apps.suppliers.validators import validate_cnpj_modulo11
from apps.tenants.models import TenantModel


class Supplier(TenantModel):
    """Fornecedores de produtos e serviços para casamentos (RF09).

    Centraliza informações cadastrais, canais de contato e histórico
    de relacionamento no nível organizacional (tenant).
    """

    objects = SupplierManager()  # type: ignore[assignment,misc]

    # Informações básicas
    name = models.CharField(
        max_length=255,
        verbose_name="Nome",
        help_text="Nome do fornecedor ou empresa",
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
        validators=[validate_cnpj_modulo11],
        verbose_name="CNPJ",
        help_text="Formato: 00.000.000/0000-00",
    )

    # Contato
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Telefone",
        help_text="Formato: (00) 00000-0000",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="E-mail",
    )
    website = models.URLField(
        blank=True,
        verbose_name="Website",
    )

    # Endereço
    address = models.TextField(
        blank=True,
        verbose_name="Endereço",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Cidade",
    )
    state = models.CharField(
        max_length=2,
        blank=True,
        verbose_name="Estado (UF)",
        validators=[MinLengthValidator(2), MaxLengthValidator(2)],
    )

    # Gestão (RF09)
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
        help_text="Anotações internas sobre o fornecedor",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Fornecedor disponível para novos contratos",
    )

    class Meta:
        # Tabela física preservada do Bounded Context original (logistics_supplier)
        # para garantir ZERO migração de dados ou downtime no Postgres.
        db_table = "logistics_supplier"
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["company", "name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["city", "state"]),
        ]

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        """Valida invariantes do modelo de fornecedor."""
        super().clean()
        if self.cnpj:
            try:
                validate_cnpj_modulo11(self.cnpj)
            except ValidationError as exc:
                raise ValidationError({"cnpj": exc.messages}) from exc

    def activate(self) -> None:
        """Ativa o fornecedor para novos contratos."""
        self.is_active = True

    def deactivate(self) -> None:
        """Desativa o fornecedor impedindo novos contratos."""
        self.is_active = False
