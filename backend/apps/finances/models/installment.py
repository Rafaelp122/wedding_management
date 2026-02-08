"""
Modelo de Parcelas do domínio financeiro.

Responsabilidade: Gestão de parcelamentos de despesas, incluindo vencimentos e status
de pagamento.

Referência: RF04
"""

from django.db import models

from apps.core.models import BaseModel, WeddingOwnedModel

from . import Expense


class Installment(BaseModel, WeddingOwnedModel):
    """
    Parcelamento (RF04).
    Dados puros de vencimento e status.
    """

    class StatusChoices(models.TextChoices):
        PAID = "PAID", "Pago"
        PENDING = "PENDING", "Pendente"
        OVERDUE = "OVERDUE", "Atrasado"

    expense = models.ForeignKey(
        Expense, on_delete=models.CASCADE, related_name="installments"
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
        unique_together = [["expense", "installment_number"]]
        ordering = ["due_date"]

    def __str__(self):
        total = self.expense.installments.count()
        return (
            f"Parcela {self.installment_number}/{total} - {self.get_status_display()}"
        )

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
        self.full_clean()
        super().save(*args, **kwargs)
