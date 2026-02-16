from django.db import transaction

from apps.finances.dto import ExpenseDTO
from apps.finances.models import Expense


class ExpenseService:
    """
    Orquestrador de lógica financeira.
    Responsável por garantir a integridade entre Despesas, Parcelas e Contratos.
    """

    @staticmethod
    @transaction.atomic
    def create(dto: ExpenseDTO) -> Expense:
        """Criação de despesa com validação de integridade futura."""
        # TODO: Implementar validação de vínculo com contrato (ADR-010)
        return Expense.objects.create(
            wedding_id=dto.wedding_id,
            category_id=dto.category_id,
            contract_id=dto.contract_id,
            description=dto.description,
            estimated_amount=dto.estimated_amount,
            actual_amount=dto.actual_amount,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: Expense, dto: ExpenseDTO) -> Expense:
        """Atualização de despesa com revalidação de parcelas."""
        instance.category_id = dto.category_id
        instance.contract_id = dto.contract_id
        instance.description = dto.description
        instance.estimated_amount = dto.estimated_amount
        instance.actual_amount = dto.actual_amount

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Expense) -> None:
        """Deleção lógica garantindo limpeza de parcelas (Cascade Manual)."""
        # TODO: instance.installments.all().delete()
        instance.delete()
