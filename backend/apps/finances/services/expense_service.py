from django.core.exceptions import ValidationError
from django.db import transaction

from apps.finances.models import BudgetCategory, Expense
from apps.logistics.models import Contract


class ExpenseService:
    """
    Orquestrador de lógica financeira para Despesas.
    Garante que gastos reais respeitem o contexto do casamento e os contratos assinados.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Expense:
        """
        Cria uma despesa garantindo herança de contexto e posse.
        """
        # 1. Recuperamos a categoria pai com segurança multitenant
        category_uuid = data.pop("category", None)
        try:
            category = (
                BudgetCategory.objects.all().for_user(user).get(uuid=category_uuid)
            )
        except BudgetCategory.DoesNotExist:
            raise ValidationError({
                "category": "Categoria não encontrada ou acesso negado."
            }) from BudgetCategory.DoesNotExist

        # 2. Tratamento de Contrato (Opcional)
        contract = None
        contract_uuid = data.pop("contract", None)
        if contract_uuid:
            try:
                # O for_user garante que o Planner não use contrato de outro casamento
                contract = Contract.objects.all().for_user(user).get(uuid=contract_uuid)
            except Contract.DoesNotExist:
                raise ValidationError({
                    "contract": "Contrato não encontrado ou acesso negado."
                }) from Contract.DoesNotExist

        # 3. Injeção de Contexto e Posse (ADR-009)
        data["planner"] = user
        data["wedding"] = category.wedding
        data["category"] = category
        data["contract"] = contract

        # 4. Instanciação e Validação de Negócio
        expense = Expense(**data)

        # O full_clean() disparará:
        # - WeddingOwnedMixin: Valida se Categoria e Contrato são do mesmo Wedding.
        # - Expense.clean(): Valida se o valor da despesa bate com o contrato assinado.
        expense.full_clean()
        expense.save()
        return expense

    @staticmethod
    @transaction.atomic
    def update(instance: Expense, user, data: dict) -> Expense:
        """
        Atualiza a despesa protegendo a integridade dos vínculos.
        """
        # Bloqueamos a troca de Casamento, Dono ou Categoria pai via API
        data.pop("planner", None)
        data.pop("wedding", None)
        data.pop("category", None)

        # Se houver troca de contrato, validamos o acesso ao novo
        if "contract" in data:
            contract_uuid = data.pop("contract")
            if contract_uuid:
                try:
                    instance.contract = (
                        Contract.objects.all().for_user(user).get(uuid=contract_uuid)
                    )
                except Contract.DoesNotExist:
                    raise ValidationError({
                        "contract": "Contrato inválido ou acesso negado."
                    }) from Contract.DoesNotExist
            else:
                instance.contract = None

        # Atualização dinâmica de campos (description, estimated_amount, actual_amount)
        for field, value in data.items():
            setattr(instance, field, value)

        # Revalida as regras de Tolerância Zero e Consistência de Contrato
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Expense) -> None:
        """
        Deleção real (Hard Delete).
        Como removemos o Soft Delete, o banco limpa as parcelas via CASCADE.
        """
        # Se você definiu on_delete=models.CASCADE nas Installments (Parcelas),
        # a deleção da despesa limpará o financeiro automaticamente.
        instance.delete()
