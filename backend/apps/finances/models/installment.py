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
    Parcela financeira vinculada a uma despesa (RF04).

    Encapsula valores, cronograma de vencimento, máquina de estados e imutabilidade de parcelas pagas.
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
        return f"Parcela {self.installment_number} - {self.expense.description} ({self.status})"

    def clean(self) -> None:
        """Valida consistência entre data de pagamento e status, além da imutabilidade de parcelas pagas (BR-F04)."""
        super().clean()

        if self.amount is not None and self.amount < 0:
            raise ValidationError(
                {
                    "amount": (
                        f"O valor da parcela não pode ser negativo; recebido: R$ {self.amount}, "
                        "esperado: >= R$ 0,00."
                    )
                }
            )

        if self.paid_date and self.status != self.StatusChoices.PAID:
            raise ValidationError(
                f"Parcela com data de pagamento ({self.paid_date}) deve ter status PAGO; "
                f"status atual: '{self.status}'."
            )

        if self.status == self.StatusChoices.PAID and not self.paid_date:
            raise ValidationError(
                f"Parcela PAGA precisa ter data de pagamento preenchida; "
                f"recebido: {self.paid_date} para status '{self.status}'."
            )

        # BR-F06: Imutabilidade de parcelas pagas
        if not self.pk:
            return

        orig = (
            Installment.objects.filter(pk=self.pk)
            .values("status", "amount", "due_date", "installment_number")
            .first()
        )
        if not orig or orig["status"] != self.StatusChoices.PAID:
            return

        changed_fields = []
        if self.amount != orig["amount"]:
            changed_fields.append(
                f"amount (atual: {orig['amount']}, novo: {self.amount})"
            )
        if self.due_date != orig["due_date"]:
            changed_fields.append(
                f"due_date (atual: {orig['due_date']}, novo: {self.due_date})"
            )
        if self.installment_number != orig["installment_number"]:
            changed_fields.append(
                f"installment_number (atual: {orig['installment_number']}, novo: {self.installment_number})"
            )

        if changed_fields:
            raise ValidationError(
                "Parcelas pagas não podem ter valor, vencimento ou número "
                f"alterados. Campos modificados: [{', '.join(changed_fields)}]. "
                "Faça a reversão antes de ajustar."
            )

    # ── Métodos de Domínio e Ciclo de Vida da Entidade ──────────────────

    def validate_chronology(self, new_due_date: date) -> None:
        """
        Valida a ordenação cronológica estrita em relação às parcelas vizinhas (BR-F05).

        Args:
            new_due_date: Nova data de vencimento proposta.

        Raises:
            BusinessRuleViolation: Se a data violar a sequência temporal com parcelas adjacentes.
        """
        if not self.expense_id or not self.installment_number:
            return

        prev = (
            Installment.objects.filter(
                expense_id=self.expense_id,
                installment_number__lt=self.installment_number,
            )
            .exclude(pk=self.pk)
            .order_by("-installment_number")
            .first()
        )
        if prev and new_due_date < prev.due_date:
            raise BusinessRuleViolation(
                detail=(
                    f"A data de vencimento ({new_due_date}) não pode ser anterior à "
                    f"parcela #{prev.installment_number} ({prev.due_date}); esperado: >= {prev.due_date}."
                ),
                code="due_date_before_previous_installment",
            )

        nxt = (
            Installment.objects.filter(
                expense_id=self.expense_id,
                installment_number__gt=self.installment_number,
            )
            .exclude(pk=self.pk)
            .order_by("installment_number")
            .first()
        )
        if nxt and new_due_date > nxt.due_date:
            raise BusinessRuleViolation(
                detail=(
                    f"A data de vencimento ({new_due_date}) não pode ser posterior à "
                    f"parcela #{nxt.installment_number} ({nxt.due_date}); esperado: <= {nxt.due_date}."
                ),
                code="due_date_after_next_installment",
            )

    def can_transition_to(self, target_status: str | StatusChoices) -> bool:
        """
        Verifica se a transição para o status informado é permitida pela máquina de estados.

        Args:
            target_status: Status de destino a ser avaliado.

        Returns:
            Verdadeiro se a transição for permitida, falso caso contrário.
        """
        target = str(target_status)
        return target in self.ALLOWED_TRANSITIONS.get(self.status, set())

    def transition_to(self, target_status: str | StatusChoices) -> None:
        """
        Executa a transição de status da parcela validando a máquina de estados.

        Args:
            target_status: Status de destino desejado.

        Raises:
            BusinessRuleViolation: Se a transição for inválida na máquina de estados.
        """
        target = str(target_status)
        if self.status == target:
            return

        if not self.can_transition_to(target):
            allowed = sorted(
                str(s) for s in self.ALLOWED_TRANSITIONS.get(self.status, set())
            )
            raise BusinessRuleViolation(
                detail=(
                    f"Transição inválida: Não é permitido transitar de '{self.status}' para '{target}'; "
                    f"opções válidas: {allowed}."
                ),
                code="installment_invalid_status_transition",
            )

        self.status = target

    def mark_as_paid(self, *, paid_date: date | None = None) -> None:
        """
        Marca a parcela como paga registrando a data de liquidação.

        Args:
            paid_date: Data opcional do pagamento (se omitida, utiliza a data corrente).

        Raises:
            BusinessRuleViolation: Se a parcela já estiver marcada como paga.
        """
        if self.status == self.StatusChoices.PAID:
            allowed = [self.StatusChoices.PENDING, self.StatusChoices.OVERDUE]
            raise BusinessRuleViolation(
                detail=(
                    f"Esta parcela já foi marcada como paga; status atual: '{self.status}', "
                    f"esperados para pagamento: {allowed}."
                ),
                code="installment_already_paid",
            )
        self.paid_date = paid_date or date.today()
        self.transition_to(self.StatusChoices.PAID)

    def unmark_as_paid(self) -> None:
        """
        Reverte o pagamento da parcela, restaurando o status adequado ao vencimento.

        Raises:
            BusinessRuleViolation: Se a parcela não estiver com status pago.
        """
        if self.status != self.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail=(
                    "Apenas parcelas marcadas como pagas podem ser desmarcadas; "
                    f"status atual: '{self.status}', esperado: '{self.StatusChoices.PAID}'."
                ),
                code="installment_not_paid",
            )
        self.paid_date = None
        if self.due_date < date.today():
            self.transition_to(self.StatusChoices.OVERDUE)
        else:
            self.transition_to(self.StatusChoices.PENDING)

    def mark_as_overdue(self) -> None:
        """
        Transiciona a parcela pendente para atrasada caso o vencimento tenha expirado.

        Raises:
            BusinessRuleViolation: Se a data de vencimento for igual ou posterior à data corrente.
        """
        today = date.today()
        if self.due_date >= today:
            raise BusinessRuleViolation(
                detail=(
                    "Apenas parcelas vencidas podem ter status alterado para atrasado; "
                    f"vencimento recebido: {self.due_date}, data de referência: {today} (esperado: < {today})."
                ),
                code="installment_not_overdue",
            )
        self.transition_to(self.StatusChoices.OVERDUE)

    # ── Propriedades de Domínio com Consumidores Ativos ─────────────────

    @property
    def is_late(self) -> bool:
        """Indica se a parcela está pendente e com vencimento ultrapassado."""
        return (
            self.status == self.StatusChoices.PENDING and self.due_date < date.today()
        )
