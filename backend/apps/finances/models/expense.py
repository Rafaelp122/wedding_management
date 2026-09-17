"""
Modelo de Despesas do domínio financeiro.

Responsabilidade: Gestão de despesas vinculadas a categorias orçamentárias e contratos.

Referências: RF04, RF05
"""

import datetime as dt
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.finances.managers import ExpenseManager
from apps.tenants.models import TenantModel


class Expense(TenantModel, WeddingOwnedMixin):
    """
    Compromisso financeiro real (RF03/RF04).
    Liga o financeiro à logística (Contract).
    """

    objects = ExpenseManager()  # type: ignore[misc]

    category = models.ForeignKey(
        "finances.BudgetCategory", on_delete=models.PROTECT, related_name="expenses"
    )
    contract = models.OneToOneField(
        "logistics.Contract",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="expense",
    )
    name = models.CharField(max_length=255, default="")
    description = models.TextField(blank=True, default="")
    estimated_amount = models.DecimalField(max_digits=10, decimal_places=2)
    actual_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0.00")
    )

    class Meta:
        app_label = "finances"
        verbose_name = "Despesa"
        verbose_name_plural = "Despesas"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return self.name or f"Despesa #{self.pk}"

    def clean(self) -> None:
        """
        Valida a regra de Tolerância Zero (BR-F01 / ADR-010).

        A verificação só roda para instâncias já persistidas (self.pk existe)
        porque durante a criação as parcelas ainda não existem — elas são
        geradas posteriormente por InstallmentService.auto_generate_installments()
        no service layer (ExpenseService.create).

        O guard self.pk previne um falso positivo no primeiro save, onde
        a soma das parcelas seria 0 e actual_amount > 0.
        """
        super().clean()

        if self.pk and self.actual_amount:
            total_installments = self.installments.aggregate(models.Sum("amount"))[
                "amount__sum"
            ] or Decimal("0.00")
            if total_installments != self.actual_amount:
                raise ValidationError(
                    f"ERRO DE INTEGRIDADE: A soma das parcelas (R${total_installments})"
                    f" não bate com o valor total (R${self.actual_amount})."
                )

        # BR-F02: Valor da despesa vinculado ao valor do contrato
        if self.contract and self.actual_amount is not None:
            if self.actual_amount != self.contract.total_amount:
                raise ValidationError(
                    f"BR-F02: O valor da despesa (R${self.actual_amount}) "
                    f"deve ser igual ao valor do contrato "
                    f"(R${self.contract.total_amount})."
                )

        # Fronteira Cross-Wedding entre contrato e despesa
        if (
            self.contract
            and self.wedding_id
            and self.contract.wedding_id != self.wedding_id
        ):
            raise ValidationError(
                "O contrato vinculado deve pertencer ao mesmo casamento da despesa."
            )

    # ── Operações de Domínio e Divisão Financeira ───────────────────────

    def calculate_installment_splits(
        self, num_installments: int, first_due_date: dt.date
    ) -> list[tuple[int, Decimal, dt.date]]:
        """
        Calcula a divisão centesimal das parcelas com ajuste na última parcela.

        Args:
            num_installments: Quantidade de parcelas (> 0).
            first_due_date: Data de vencimento da primeira parcela.

        Returns:
            list[tuple[int, Decimal, dt.date]]: Lista com (número, valor, vencimento).

        Raises:
            BusinessRuleViolation: Se as parcelas forem <= 0 ou o valor for inválido.
        """
        from datetime import timedelta

        if num_installments <= 0:
            raise BusinessRuleViolation(
                detail="O número de parcelas deve ser maior que zero.",
                code="invalid_installment_number",
            )
        if not self.actual_amount or self.actual_amount <= Decimal("0.00"):
            raise BusinessRuleViolation(
                detail="A despesa precisa ter valor maior que zero para parcelamento.",
                code="invalid_expense_amount",
            )

        base_amount = round(self.actual_amount / num_installments, 2)
        splits: list[tuple[int, Decimal, dt.date]] = []
        current_date = first_due_date

        for i in range(1, num_installments):
            splits.append((i, base_amount, current_date))
            current_date += timedelta(days=30)

        last_amount = self.actual_amount - (base_amount * (num_installments - 1))
        splits.append((num_installments, last_amount, current_date))
        return splits

    # ── Propriedades de Domínio ──────────────────────────────────────────

    @property
    def has_paid_installments(self) -> bool:
        """Indica se a despesa possui pelo menos uma parcela com status PAID."""
        paid_count = getattr(self, "paid_installments_count", None)
        if paid_count is not None:
            return bool(paid_count > 0)
        from apps.finances.models.installment import Installment

        return self.installments.filter(status=Installment.StatusChoices.PAID).exists()

    @property
    def first_due_date(self) -> dt.date | None:
        """Retorna a data de vencimento da primeira parcela cadastrada, se houver."""
        first = self.installments.order_by("installment_number").first()
        return first.due_date if first else None

    @property
    def status(self) -> str:
        """Calcula o status dinâmico da despesa a partir de suas parcelas."""
        total = getattr(self, "installments_count", None)
        if total is None:
            total = self.installments.count()

        paid = getattr(self, "paid_installments_count", None)
        if paid is None:
            paid = self.installments.filter(status="PAID").count()

        if total == 0:
            return "PENDING"
        if paid >= total:
            return "SETTLED"
        if paid > 0:
            return "PARTIALLY_PAID"
        return "PENDING"

    @property
    def payment_progress_percent(self) -> int:
        """Percentual do valor pago em relação ao valor total da despesa (0 a 100)."""
        if not self.actual_amount or self.actual_amount <= Decimal("0.00"):
            return 0
        total_paid = getattr(self, "total_paid", None)
        if total_paid is None:
            from apps.finances.models.installment import Installment

            total_paid = self.installments.filter(
                status=Installment.StatusChoices.PAID
            ).aggregate(models.Sum("amount"))["amount__sum"] or Decimal("0.00")
        percent = int((total_paid / self.actual_amount) * 100)
        return min(100, max(0, percent))
