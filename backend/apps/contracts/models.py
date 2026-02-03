from django.db import models

from apps.core.models import BaseModel
from apps.items.models import Item


class Contract(BaseModel):
    """Modelo simplificado de Contrato."""

    class StatusChoices(models.TextChoices):
        DRAFT = "DRAFT", "Rascunho"
        PENDING = "PENDING", "Pendente"
        SIGNED = "SIGNED", "Assinado"
        CANCELED = "CANCELED", "Cancelado"

    item = models.OneToOneField(Item, on_delete=models.CASCADE, related_name="contract")
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
    )

    # RF10: Alertas de vencimento
    expiration_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Vencimento",
        help_text="Data de expiração do contrato",
    )
    alert_days_before = models.PositiveIntegerField(
        default=30,
        verbose_name="Alertar Dias Antes",
        help_text="Quantos dias antes do vencimento enviar alerta",
    )

    # Assinatura do planner
    planner_signed_at = models.DateTimeField(null=True, blank=True)

    # Assinatura do fornecedor
    supplier_signed_at = models.DateTimeField(null=True, blank=True)

    # Assinatura dos noivos
    couple_signed_at = models.DateTimeField(null=True, blank=True)

    # PDF final do contrato
    pdf_file = models.FileField(upload_to="contracts/%Y/%m/", null=True, blank=True)

    class Meta:
        verbose_name = "Contrato"
        verbose_name_plural = "Contratos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Contrato - {self.item.name}"

    @property
    def is_fully_signed(self):
        """Verifica se todas as partes assinaram."""
        return all(
            [
                self.planner_signed_at,
                self.supplier_signed_at,
                self.couple_signed_at,
            ]
        )
