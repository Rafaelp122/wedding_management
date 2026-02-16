from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.finances.dto import InstallmentDTO
from apps.finances.models import Expense, Installment


class InstallmentService:
    """
    Orquestrador de parcelas.
    Implementa cálculos automáticos de status e validação de Tolerância Zero.
    """

    @staticmethod
    def determine_status(due_date: date, paid_date: date | None) -> str:
        """Lógica de negócio para definir status da parcela."""
        if paid_date:
            return Installment.StatusChoices.PAID
        if due_date < date.today():
            return Installment.StatusChoices.OVERDUE
        return Installment.StatusChoices.PENDING

    @staticmethod
    @transaction.atomic
    def create(dto: InstallmentDTO) -> Installment:
        # Recuperamos a despesa pai para garantir o Multitenancy
        expense = Expense.objects.get(uuid=dto.expense_id)

        status = InstallmentService.determine_status(dto.due_date, dto.paid_date)

        installment = Installment.objects.create(
            wedding=expense.wedding,  # Herda o casamento da despesa
            expense=expense,
            installment_number=dto.installment_number,
            amount=dto.amount,
            due_date=dto.due_date,
            paid_date=dto.paid_date,
            status=status,
            notes=dto.notes,
        )

        # Trigger ADR-010: Força a validação de soma na Despesa pai
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict) from e

        return installment

    @staticmethod
    @transaction.atomic
    def update(instance: Installment, dto: InstallmentDTO) -> Installment:
        instance.amount = dto.amount
        instance.due_date = dto.due_date
        instance.paid_date = dto.paid_date
        instance.notes = dto.notes
        instance.status = InstallmentService.determine_status(
            dto.due_date, dto.paid_date
        )

        instance.save()

        # Após atualizar a parcela, validamos se a soma na Expense ainda bate
        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict) from e

        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Installment) -> None:
        expense = instance.expense
        instance.delete()

        # Validamos se a remoção da parcela não deixou a despesa inconsistente
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict) from e
