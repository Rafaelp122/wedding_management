from apps.core.models import BaseModel
from django.core.validators import MaxLengthValidator, MinValueValidator
from django.db import models


class Supplier(BaseModel):
    """
    Fornecedores de produtos e serviços para casamentos.
    Centraliza informações de contato e histórico de relacionamento.
    """

    # Informações básicas
    name = models.CharField(
        max_length=255,
        verbose_name="Nome",
        help_text="Nome do fornecedor ou empresa",
    )
    cnpj = models.CharField(
        max_length=18,
        blank=True,
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
        validators=[MaxLengthValidator(2)],
    )

    # Avaliação e gestão
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0)],
        verbose_name="Avaliação",
        help_text="Nota de 0.0 a 5.0",
    )
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
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"
        ordering = ["name"]
        indexes = [
            models.Index(fields=["name"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["city", "state"]),
        ]

    def __str__(self):
        return self.name

    @property
    def full_address(self):
        """Retorna endereço completo formatado."""
        parts = [self.address, self.city]
        if self.state:
            parts.append(self.state)
        return ", ".join(filter(None, parts))
