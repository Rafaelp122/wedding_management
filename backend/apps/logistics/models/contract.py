"""
Modelo de Contratos do domínio logístico.

Responsabilidade: Gestão de contratos com fornecedores, incluindo valores, prazos e
documentação.

Referências: RF10, RF13
"""

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.validators import MaxFileSizeValidator
from apps.tenants.models import TenantModel


class Contract(TenantModel, WeddingOwnedMixin):
    # Override WeddingOwnedMixin.wedding from CASCADE → PROTECT
    wedding = models.ForeignKey(
        "weddings.Wedding",
        on_delete=models.PROTECT,
        related_name="%(class)s_records",
    )

    class StatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING = "PENDING", "Pendente"  # Aguardando assinaturas externas
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    supplier = models.ForeignKey(
        "logistics.Supplier",
        on_delete=models.CASCADE,
        related_name="contracts",
        verbose_name="Fornecedor",
    )

    # O VALOR DE FACE: Essencial para o Controle Máximo
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Valor Total do Contrato",
        help_text="Valor exato que consta no documento assinado",
    )

    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(
        blank=True, default="", verbose_name="Descrição do Contrato"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    # Controle de prazos (RF13)
    expiration_date = models.DateField(null=True, blank=True)
    alert_days_before = models.PositiveIntegerField(default=30)

    # Metadados de Assinatura (Opcional - Controle Manual)
    # Como o sistema não assina, essas datas são preenchidas manualmente pelo Planner
    signed_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data da Assinatura",
        help_text="Data em que o contrato foi formalizado externamente",
    )

    pdf_file = models.FileField(
        upload_to="contracts/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="Arquivo PDF",
        help_text="Formatos aceitos: PDF, PNG, JPEG. Tamanho máximo: 10MB.",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["pdf", "png", "jpg", "jpeg"],
                message="Tipo de arquivo não suportado. Use PDF, PNG ou JPEG.",
            ),
            MaxFileSizeValidator(max_size=10 * 1024 * 1024),
        ],
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="addendums",
        verbose_name="Contrato Original (Pai)",
        help_text="Vincula este contrato como aditivo de um contrato principal.",
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        name = self.name or "Contrato"
        return (
            f"{name} - {self.supplier.name} ({self.wedding}) - R$ {self.total_amount}"
        )

    def clean(self) -> None:
        super().clean()

        # Não existe contrato assinado sem dinheiro e sem papel
        if self.status == self.StatusChoices.SIGNED:
            if not self.pdf_file:
                raise ValidationError(
                    "Um contrato marcado como ASSINADO exige o upload do arquivo PDF."
                )
            if not self.total_amount or self.total_amount <= 0:
                raise ValidationError(
                    "Um contrato marcado como ASSINADO deve ter um valor total "
                    "positivo."
                )
            if not self.signed_date:
                raise ValidationError("Informe a data em que o contrato foi assinado.")
