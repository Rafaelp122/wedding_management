"""
Modelo de Parcelas do domínio financeiro.

Responsabilidade: Gestão de parcelamentos de despesas, incluindo vencimentos e status
de pagamento.

Referência: RF04
"""

from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.models import BaseModel


class Installment(BaseModel, WeddingOwnedMixin):
    """
    Parcelamento (RF04).
    Representa uma fatia financeira de uma Despesa.
    """

    class StatusChoices(models.TextChoices):
        PAID = "PAID", "Pago"
        PENDING = "PENDING", "Pendente"
        OVERDUE = "OVERDUE", "Atrasado"

    # Relacionamento forte com a Despesa
    expense = models.ForeignKey(
        "finances.Expense", on_delete=models.CASCADE, related_name="installments"
    )

    installment_number = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING
    )
    notes = models.TextField(blank=True)

    class Meta:
        app_label = "finances"
        # Garante que não existam duas parcelas com o mesmo número para a mesma despesa
        unique_together = [["expense", "installment_number"]]
        ordering = ["due_date"]
        indexes = [
            models.Index(fields=["status", "due_date"]),
        ]

    def __str__(self):
        return f"Parcela {self.installment_number} - {self.expense.description} ({self.status})"  # noqa

    def clean(self):
        """Validações de consistência paid_date ↔ status."""
        super().clean()
        from django.core.exceptions import ValidationError

        if self.paid_date and self.status != self.StatusChoices.PAID:
            raise ValidationError("Parcela com data de pagamento deve ter status PAGO")

        if self.status == self.StatusChoices.PAID and not self.paid_date:
            raise ValidationError(
                "Parcela PAGA precisa ter data de pagamento preenchida"
            )

    def save(self, *args, **kwargs):
        """Garante a execução das validações do clean antes de persistir."""
        self.full_clean()
        super().save(*args, **kwargs)
