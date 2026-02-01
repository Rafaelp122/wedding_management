from decimal import Decimal

from apps.users.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum


class Wedding(models.Model):
    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "IN_PROGRESS", "Em Andamento"
        COMPLETED = "COMPLETED", "Concluído"
        CANCELED = "CANCELED", "Cancelado"

    planner = models.ForeignKey(User, on_delete=models.CASCADE)
    groom_name = models.CharField(max_length=100)
    bride_name = models.CharField(max_length=100)
    date = models.DateField()
    location = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Casamento"
        verbose_name_plural = "Casamentos"
        ordering = ["-date"]
        indexes = [
            models.Index(fields=["planner", "status"]),
            models.Index(fields=["date"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.groom_name} & {self.bride_name}"


class Budget(models.Model):
    """
    Orçamento mestre vinculado a um casamento (RF03).
    Relação 1:1 com Wedding para centralizar o controle financeiro.
    """

    wedding = models.OneToOneField(
        Wedding,
        on_delete=models.CASCADE,
        related_name="budget",
        verbose_name="Casamento",
    )
    total_estimated = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Valor Estimado Total",
        help_text="Orçamento planejado total para o evento",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Observações",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Orçamento"
        verbose_name_plural = "Orçamentos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Orçamento - {self.wedding}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve save() para criar categorias padrão automaticamente (RF03).
        """
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            # Categorias padrão com sugestão de distribuição (percentual aproximado)
            default_categories = [
                {
                    "name": "Buffet",
                    "description": "Alimentação e bebidas",
                    "weight": Decimal("0.35"),
                },
                {
                    "name": "Local",
                    "description": "Aluguel e infraestrutura do local",
                    "weight": Decimal("0.20"),
                },
                {
                    "name": "Decoração",
                    "description": "Flores, arranjos e decoração",
                    "weight": Decimal("0.15"),
                },
                {
                    "name": "Fotografia e Vídeo",
                    "description": "Registro profissional do evento",
                    "weight": Decimal("0.10"),
                },
                {
                    "name": "Música/Entretenimento",
                    "description": "DJ, banda ou outros entretenimentos",
                    "weight": Decimal("0.10"),
                },
                {
                    "name": "Vestuário",
                    "description": "Trajes dos noivos e padrinhos",
                    "weight": Decimal("0.05"),
                },
                {
                    "name": "Outros",
                    "description": "Despesas diversas",
                    "weight": Decimal("0.05"),
                },
            ]

            for category_data in default_categories:
                allocated_amount = self.total_estimated * category_data["weight"]
                BudgetCategory.objects.create(
                    budget=self,
                    name=category_data["name"],
                    description=category_data["description"],
                    allocated_budget=allocated_amount,
                )

    @property
    def total_spent(self):
        """Calcula o total gasto somando todos os itens (RF05)."""
        return self.categories.aggregate(
            total=Sum("items__actual_cost", filter=Q(items__actual_cost__gt=0))
        )["total"] or Decimal("0.00")

    @property
    def total_paid(self):
        """Calcula o total pago somando todas as parcelas pagas (RF04)."""
        from apps.items.models import Installment

        return Installment.objects.filter(
            item__budget_category__budget=self, status="PAID"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def total_pending(self):
        """Calcula o total pendente (RF04)."""
        from apps.items.models import Installment

        return Installment.objects.filter(
            item__budget_category__budget=self, status="PENDING"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def total_overdue(self):
        """Calcula o total atrasado (RF04)."""
        from apps.items.models import Installment

        return Installment.objects.filter(
            item__budget_category__budget=self, status="OVERDUE"
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def financial_health(self):
        """
        Retorna a saúde financeira do evento (RF05).
        Percentual: (gasto / estimado) * 100
        """
        if self.total_estimated == 0:
            return Decimal("0.00")
        return (self.total_spent / self.total_estimated) * 100

    @property
    def remaining_budget(self):
        """Retorna o saldo restante do orçamento."""
        return self.total_estimated - self.total_spent


class BudgetCategory(models.Model):
    """
    Categorias de gastos do orçamento (RF03).
    Exemplos: Buffet, Decoração, Fotografia, Música, etc.
    """

    budget = models.ForeignKey(
        Budget,
        on_delete=models.CASCADE,
        related_name="categories",
        verbose_name="Orçamento",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="Nome da Categoria",
        help_text="Ex: Buffet, Decoração, Fotografia",
    )
    description = models.TextField(
        blank=True,
        verbose_name="Descrição",
    )
    allocated_budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name="Orçamento Alocado",
        help_text="Quanto foi reservado para esta categoria",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Categoria de Orçamento"
        verbose_name_plural = "Categorias de Orçamento"
        ordering = ["name"]
        unique_together = [["budget", "name"]]

    def __str__(self):
        return f"{self.name} - {self.budget.wedding}"

    @property
    def total_spent(self):
        """Calcula o total gasto nesta categoria."""
        return self.items.aggregate(
            total=Sum("actual_cost", filter=Q(actual_cost__gt=0))
        )["total"] or Decimal("0.00")

    @property
    def remaining_budget(self):
        """Retorna o saldo restante da categoria."""
        return self.allocated_budget - self.total_spent
