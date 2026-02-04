from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models

from apps.core.models import BaseModel, SoftDeleteModel


class Budget(BaseModel):
    """
    Orçamento mestre (RF03).
    Apenas a âncora financeira do casamento.
    """

    wedding = models.OneToOneField(
        "weddings.Wedding", on_delete=models.CASCADE, related_name="budget"
    )
    total_estimated = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Orçamento"
        ordering = ["-created_at"]


class BudgetCategory(SoftDeleteModel):
    """
    Categorias de gastos (RF03).
    O SoftDelete aqui serve apenas para histórico, não para lógica de soma.
    """

    budget = models.ForeignKey(
        Budget, on_delete=models.CASCADE, related_name="categories"
    )
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    allocated_budget = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal("0.00"))]
    )

    class Meta:
        unique_together = [["budget", "name"]]
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} - {self.budget.wedding}"


class Expense(BaseModel):
    """
    Compromisso financeiro real (RF03/RF04).
    Liga o financeiro à logística (Contract).
    """

    category = models.ForeignKey(
        BudgetCategory, on_delete=models.PROTECT, related_name="expenses", db_index=True
    )
    # Referência opcional para logística
    contract = models.OneToOneField(
        "logistics.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense",
    )
    description = models.CharField(max_length=255)
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.description} - {self.category.name} - R${self.actual_amount}"

    def clean(self):
        """Validações de negócio."""
        super().clean()

        # Valida soma das parcelas se despesa já existe
        if self.pk and self.actual_amount:
            total_installments = self.installments.aggregate(models.Sum("amount"))[
                "amount__sum"
            ] or Decimal("0.00")

            if abs(total_installments - self.actual_amount) > Decimal("0.01"):
                from django.core.exceptions import ValidationError

                raise ValidationError(
                    f"Soma das parcelas (R${total_installments}) difere do valor total "
                    f"(R${self.actual_amount})"
                )


class Installment(BaseModel):
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
