"""
Modelo de Parcelas do domínio financeiro.

Responsabilidade: Gestão de parcelamentos de despesas, incluindo vencimentos e status
de pagamento.

Referência: RF04
"""

from datetime import date
from typing import ClassVar

from django.core.exceptions import ValidationError
from django.db import models

from apps.core.exceptions import BusinessRuleViolation
from apps.core.mixins import WeddingOwnedMixin
from apps.finances.managers import InstallmentManager
from apps.tenants.models import TenantModel


class Installment(TenantModel, WeddingOwnedMixin):
    """
    Parcelamento (RF04).
    Representa uma fatia financeira de uma Despesa.
    """

    objects = InstallmentManager()  # type: ignore[misc]

    class StatusChoices(models.TextChoices):
        PAID = "PAID", "Pago"
        PENDING = "PENDING", "Pendente"
        OVERDUE = "OVERDUE", "Atrasado"

    ALLOWED_TRANSITIONS: ClassVar[dict[str, set[str]]] = {
        StatusChoices.PENDING: {StatusChoices.PAID, StatusChoices.OVERDUE},
        StatusChoices.OVERDUE: {StatusChoices.PAID, StatusChoices.PENDING},
        StatusChoices.PAID: {StatusChoices.PENDING, StatusChoices.OVERDUE},
    }

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
            models.Index(fields=["company", "wedding"]),
            models.Index(fields=["status", "due_date"]),
        ]

    def __str__(self) -> str:
        return f"Parcela {self.installment_number} - {self.expense.description} ({self.status})"  # noqa

    def clean(self) -> None:
        """Validações de consistência paid_date ↔ status."""
        super().clean()

        if self.amount is not None and self.amount < 0:
            raise ValidationError(
                {"amount": "O valor da parcela não pode ser negativo."}
            )

        if self.paid_date and self.status != self.StatusChoices.PAID:
            raise ValidationError("Parcela com data de pagamento deve ter status PAGO")

        if self.status == self.StatusChoices.PAID and not self.paid_date:
            raise ValidationError(
                "Parcela PAGA precisa ter data de pagamento preenchida"
            )

    # ── Métodos de Ciclo de Vida da Entidade ─────────────────────────────

    def can_transition_to(self, target_status: str | StatusChoices) -> bool:
        """Verifica se a transição para o status informado é válida.

        Args:
            target_status: Status de destino a ser avaliado.

        Returns:
            True se a transição for permitida, False caso contrário.
        """
        target = str(target_status)
        return target in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, target_status: str | StatusChoices) -> None:
        """Executa a transição de status da parcela validando as regras do domínio.

        Args:
            target_status: Status de destino desejado.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
        """
        target = str(target_status)
        if self.status == target:
            return

        if not self.can_transition_to(target):
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{self.status}' para '{target}'.",
                code="installment_invalid_status_transition",
            )

        self.status = target

    def mark_as_paid(self, *, paid_date: date | None = None) -> None:
        """Marca a parcela como paga com a data informada ou atual.

        Args:
            paid_date: Data opcional do pagamento. Se omitida, utiliza a data atual.

        Raises:
            BusinessRuleViolation: Se a parcela já estiver marcada como paga.
        """
        if self.status == self.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail="Esta parcela já foi marcada como paga.",
                code="installment_already_paid",
            )
        self.paid_date = paid_date or date.today()
        self.transition_to(self.StatusChoices.PAID)

    def unmark_as_paid(self) -> None:
        """Desmarca o pagamento da parcela, restaurando o status adequado ao vencimento.

        Raises:
            BusinessRuleViolation: Se a parcela não estiver marcada como paga.
        """
        if self.status != self.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail="Apenas parcelas marcadas como pagas podem ser desmarcadas.",
                code="installment_not_paid",
            )
        self.paid_date = None
        if self.due_date < date.today():
            self.transition_to(self.StatusChoices.OVERDUE)
        else:
            self.transition_to(self.StatusChoices.PENDING)

    def mark_as_overdue(self) -> None:
        """Altera status para atrasado caso a data de vencimento tenha passado.

        Raises:
            BusinessRuleViolation: Se a data de vencimento ainda não tiver passado.
        """
        if self.due_date >= date.today():
            raise BusinessRuleViolation(
                detail=(
                    "Apenas parcelas vencidas podem ter status alterado para atrasado."
                ),
                code="installment_not_overdue",
            )
        self.transition_to(self.StatusChoices.OVERDUE)

    # ── Propriedades de Conveniência ─────────────────────────────────────

    @property
    def is_paid(self) -> bool:
        """Indica se a parcela está com status PAGO."""
        return self.status == self.StatusChoices.PAID

    @property
    def is_pending(self) -> bool:
        """Indica se a parcela está com status PENDENTE."""
        return self.status == self.StatusChoices.PENDING

    @property
    def is_overdue(self) -> bool:
        """Indica se a parcela está com status ATRASADO."""
        return self.status == self.StatusChoices.OVERDUE

    @property
    def is_late(self) -> bool:
        """Indica se a parcela está pendente e com vencimento ultrapassado."""
        return self.is_pending and self.due_date < date.today()

    @property
    def days_overdue(self) -> int:
        """Número de dias em atraso em relação à data atual."""
        if self.due_date < date.today():
            return (date.today() - self.due_date).days
        return 0

    @property
    def days_until_due(self) -> int:
        """Número de dias restantes até a data de vencimento."""
        if self.due_date >= date.today():
            return (self.due_date - date.today()).days
        return 0
