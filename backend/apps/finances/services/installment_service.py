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
        """Cria uma parcela garantindo herança de contexto e validação de ADR-010."""
        # Recuperamos a despesa pai para garantir o Multitenancy
        expense = Expense.objects.get(uuid=dto.expense_id)

        # Preparamos os dados do DTO e injetamos o status calculado
        data = dto.model_dump()
        data["status"] = InstallmentService.determine_status(
            dto.due_date, dto.paid_date
        )

        # Removemos expense_id para passar o objeto expense explicitamente
        # (garante wedding)
        data.pop("expense_id")

        installment = Installment.objects.create(
            wedding=expense.wedding,  # Herda o casamento da despesa
            expense=expense,
            **data,
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
        """Atualização de parcela com revalidação de teto da Expense."""
        # Campos que não devem ser alterados via update comum
        exclude_fields = {"planner_id", "wedding_id", "expense_id"}

        data = dto.model_dump(exclude=exclude_fields)
        data["status"] = InstallmentService.determine_status(
            dto.due_date, dto.paid_date
        )

        # Atualização dinâmica via setattr
        for field, value in data.items():
            setattr(instance, field, value)

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
        """Deleção lógica garantindo limpeza de parcelas (Cascade Manual)."""
        expense = instance.expense
        instance.delete()

        # Validamos se a remoção da parcela não deixou a despesa inconsistente
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            raise DRFValidationError(e.message_dict) from e
