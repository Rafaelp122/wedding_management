from datetime import date

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.finances.models import Expense, Installment


class InstallmentService:
    """
    Orquestrador de parcelas.
    Garante que a matemática financeira nunca minta para o Planner.
    """

    @staticmethod
    def _determine_status(due_date, paid_date) -> str:
        """Lógica centralizada para definição de status."""
        if paid_date:
            return Installment.StatusChoices.PAID
        if due_date < date.today():
            return Installment.StatusChoices.OVERDUE
        return Installment.StatusChoices.PENDING

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Installment:
        """
        Cria uma parcela e valida se ela não quebra a integridade da despesa.
        """
        expense_uuid = data.pop("expense", None)

        # 1. SEGURANÇA: Busca a despesa garantindo que o Planner é o dono.
        try:
            expense = Expense.objects.all().for_user(user).get(uuid=expense_uuid)
        except Expense.DoesNotExist:
            raise ValidationError({
                "expense": "Despesa não encontrada ou acesso negado."
            }) from Expense.DoesNotExist

        # 2. Injeção de Contexto e Status
        data["planner"] = user
        data["wedding"] = expense.wedding
        data["expense"] = expense
        data["status"] = InstallmentService._determine_status(
            data.get("due_date"), data.get("paid_date")
        )

        # 3. Criação
        installment = Installment(**data)

        # 4. VALIDAÇÃO ADR-010: O full_clean da despesa vai checar se a soma
        # agora bate (ou ainda não bate) com o valor total.
        # NOTA: Se o seu sistema exige que a soma bata SEMPRE, você não pode criar
        # parcelas uma a uma. Você precisa criá-las em lote.
        installment.full_clean()
        installment.save()

        # Forçamos a revalidação da despesa pai
        expense.full_clean()

        return installment

    @staticmethod
    @transaction.atomic
    def update(instance: Installment, user, data: dict) -> Installment:
        """
        Atualiza a parcela e revalida o teto da Expense.
        """
        # Proteção de campos imutáveis
        data.pop("expense", None)
        data.pop("wedding", None)
        data.pop("planner", None)

        if "due_date" in data or "paid_date" in data:
            due = data.get("due_date", instance.due_date)
            paid = data.get("paid_date", instance.paid_date)
            instance.status = InstallmentService._determine_status(due, paid)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.full_clean()
        instance.save()

        # Revalidação de Tolerância Zero na Despesa
        instance.expense.full_clean()

        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Installment) -> None:
        """
        Deleção com trava de segurança financeira.
        """
        expense = instance.expense

        # Se a despesa exige soma exata (ADR-010), deletar uma parcela
        # sem deletar a despesa ou ajustar o valor total é um erro.
        instance.delete()

        # Se após a deleção a despesa ficar inconsistente, o full_clean explode.
        # O atomic garante que a deleção sofra rollback.
        expense.full_clean()
