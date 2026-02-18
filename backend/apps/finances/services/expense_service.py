from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.finances.dto import ExpenseDTO
from apps.finances.models import BudgetCategory, Expense


class ExpenseService:
    """
    Orquestrador de lógica financeira.
    Responsável por garantir a integridade entre Despesas, Parcelas e Contratos.
    """

    @staticmethod
    @transaction.atomic
    def create(dto: ExpenseDTO) -> Expense:
        """Criação de despesa com herança de contexto e validação de contrato."""

        # Busca a categoria pai para garantir o contexto (Herança de Contexto)
        category = BudgetCategory.objects.get(uuid=dto.category_id)

        contract = None
        if dto.contract_id:
            from apps.logistics.models import Contract

            contract = Contract.objects.get(uuid=dto.contract_id)

            # Garante que o contrato pertença ao mesmo casamento da categoria
            if contract.wedding_id != category.wedding_id:
                raise DjangoValidationError(
                    "O contrato selecionado pertence a outro casamento."
                )

        data = dto.model_dump()

        # Limpeza para evitar conflito de argumentos (mesma lógica das parcelas)
        data.pop("category_id")
        data.pop("contract_id", None)
        data.pop("wedding_id", None)
        data.pop("planner_id", None)

        return Expense.objects.create(
            planner=category.planner,  # Herda o dono da categoria
            wedding=category.wedding,  # Herda o casamento da categoria (Garante Multitenancy) # noqa
            category=category,
            contract=contract,
            **data,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: Expense, dto: ExpenseDTO) -> Expense:
        """Atualização de despesa com proteção de integridade."""

        # No update, impedimos a troca acidental de Categoria ou Casamento
        exclude_fields = {"planner_id", "wedding_id", "category_id"}

        data = dto.model_dump(exclude=exclude_fields)

        # Se houver troca de contrato, validamos novamente o vínculo
        if dto.contract_id and str(dto.contract_id) != str(instance.contract_id):
            from apps.logistics.models import Contract

            contract = Contract.objects.get(uuid=dto.contract_id)
            if contract.wedding_id != instance.wedding_id:
                raise DjangoValidationError(
                    "O contrato selecionado pertence a outro casamento."
                )
            instance.contract = contract

        for field, value in data.items():
            if field != "contract_id":  # Já tratado acima
                setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Expense) -> None:
        """Deleção lógica garantindo limpeza de parcelas (Cascade Manual)."""
        # TODO: instance.installments.all().delete()
        instance.delete()
