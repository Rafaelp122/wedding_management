from decimal import Decimal
from typing import ClassVar

from apps.core.models import BaseModel
from apps.weddings.models import Wedding
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum


class Item(BaseModel):
    """
    Item unificado: logística (RF06/RF07) + financeiro (RF03/RF04).
    Combina controle de aquisição com gestão financeira.
    """

    STATUS_CHOICES: ClassVar[list[tuple[str, str]]] = [
        ("PENDING", "Pendente"),
        ("IN_PROGRESS", "Em Andamento"),
        ("DONE", "Concluído"),
    ]

    # === CORE ===
    wedding = models.ForeignKey(
        Wedding,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Casamento",
    )
    name = models.CharField(max_length=255, verbose_name="Nome")
    description = models.TextField(blank=True, verbose_name="Descrição")

    # === LOGÍSTICA (RF06/RF07) ===
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="items",
        verbose_name="Fornecedor",
        help_text="Fornecedor responsável pelo item/serviço",
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="Quantidade",
        help_text="Quantidade física necessária",
    )
    acquisition_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        verbose_name="Status de Aquisição",
        help_text="Status da logística/contratação",
    )

    # === FINANCEIRO (RF03/RF04/RF05) ===
    budget_category = models.ForeignKey(
        "weddings.BudgetCategory",
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Categoria",
        help_text="Categoria do item (financeiro + logístico)",
    )
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
        verbose_name="Custo Estimado",
        help_text="Valor estimado/orçado",
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        default=Decimal("0.00"),
        verbose_name="Custo Real",
        help_text="Valor final após negociação",
    )

    class Meta:
        verbose_name = "Item"
        verbose_name_plural = "Itens"
        ordering: ClassVar[list[str]] = ["-created_at"]
        indexes: ClassVar[list[models.Index]] = [
            models.Index(fields=["wedding", "budget_category"]),
            models.Index(fields=["wedding", "acquisition_status"]),
            models.Index(fields=["budget_category"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return self.name

    @property
    def total_cost(self):
        """Custo total: quantidade X custo real (ou estimado se real = 0)."""
        cost = self.actual_cost if self.actual_cost > 0 else self.estimated_cost
        return cost * self.quantity

    @property
    def total_paid(self):
        """Total pago através de parcelas."""
        return self.installments.filter(status="PAID").aggregate(total=Sum("amount"))[
            "total"
        ] or Decimal("0.00")

    @property
    def total_pending(self):
        """Total pendente em parcelas."""
        return self.installments.filter(status="PENDING").aggregate(
            total=Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def balance(self):
        """Saldo: custo real - total pago."""
        return self.actual_cost - self.total_paid


class Installment(BaseModel):
    """
    Controle de parcelamento de pagamentos (RF04).
    Cada item pode ter múltiplas parcelas com status independentes.
    """

    class StatusChoices(models.TextChoices):
        PAID = "PAID", "Pago"
        PENDING = "PENDING", "Pendente"
        OVERDUE = "OVERDUE", "Atrasado"

    item = models.ForeignKey(
        Item,
        on_delete=models.CASCADE,
        related_name="installments",
        verbose_name="Item",
    )
    installment_number = models.PositiveIntegerField(
        verbose_name="Número da Parcela",
        help_text="Ex: 1, 2, 3...",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor da Parcela",
    )
    due_date = models.DateField(
        verbose_name="Data de Vencimento",
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Data de Pagamento",
    )
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        verbose_name="Status",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )

    class Meta:
        verbose_name = "Parcela"
        verbose_name_plural = "Parcelas"
        ordering = ["due_date", "installment_number"]
        unique_together = [["item", "installment_number"]]
        indexes = [
            models.Index(fields=["status", "due_date"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"Parcela {self.installment_number} - {self.item.name}"
