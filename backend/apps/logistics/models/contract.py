"""
Modelo de Contratos do domínio logístico.

Responsabilidade: Gestão de contratos com fornecedores, incluindo valores, prazos e
documentação.

Referências: RF10, RF13
"""

from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.models import BaseModel


class Contract(BaseModel, WeddingOwnedMixin):
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

    description = models.TextField(blank=True, verbose_name="Descrição do Contrato")
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
        upload_to="contracts/%Y/%m/", null=True, blank=True, verbose_name="Arquivo PDF"
    )

    class Meta:
        app_label = "logistics"
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Contrato {self.id} - {self.supplier.name} ({self.wedding}) "
            f"- R$ {self.total_amount}"
        )

    def clean(self):
        super().clean()
        from django.core.exceptions import ValidationError

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

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        super().save(*args, **kwargs)
