from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from apps.finances.models import Budget
from apps.weddings.models import Wedding


class BudgetService:
    """
    Camada de serviço para gestão do orçamento mestre.
    Garante que cada casamento tenha exatamente UM teto financeiro (ADR-003/009).
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Budget:
        """
        Cria o orçamento garantindo que o Casamento pertence ao Planner.
        """
        # 1. Recuperamos o casamento usando o filtro de segurança for_user
        wedding_uuid = data.pop("wedding", None)
        try:
            wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_uuid)
        except Wedding.DoesNotExist:
            raise ValidationError({
                "wedding": "Casamento não encontrado ou acesso negado."
            }) from Wedding.DoesNotExist

        # 2. Injeção de contexto
        # O Budget é OneToOne com Wedding. Se já existir, o banco lançará
        # IntegrityError.
        data["wedding"] = wedding

        try:
            budget = Budget.objects.create(**data)
        except IntegrityError:
            raise ValidationError({
                "wedding": "Este casamento já possui um orçamento definido."
            }) from IntegrityError

        return budget

    @staticmethod
    @transaction.atomic
    def update(instance: Budget, user, data: dict) -> Budget:
        """
        Atualiza o orçamento protegendo os vínculos de propriedade.
        """
        # Impedimos a troca de Casamento ou Planner via update
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() é essencial para validar MinValueValidator e outras regras
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Budget) -> None:
        """
        Executa a deleção real do orçamento (Hard Delete).
        """
        # Se você deletar o orçamento mestre, as categorias e despesas
        # vinculadas podem ficar órfãs se o on_delete não for CASCADE.
        # No seu caso, o Budget é a raiz financeira. Use com cuidado.
        instance.delete()
