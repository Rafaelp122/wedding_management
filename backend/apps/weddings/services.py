from django.db import transaction

from .models import Wedding


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.
    Focada em multitenancy e integridade real de dados.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Wedding:
        """
        Cria um novo casamento vinculado ao Planner autenticado.
        """
        # Injetamos o planner diretamente do contexto da request,
        # garantindo que ninguém crie casamentos para outros.
        data["planner"] = user

        wedding = Wedding.objects.create(**data)

        # ESPAÇO PARA EFEITOS COLATERAIS (MVP):
        # 1. Criar orçamento base automático.
        # 2. Criar categorias financeiras padrão (Buffet, Local, etc).

        return wedding

    @staticmethod
    @transaction.atomic
    def update(instance: Wedding, user, data: dict) -> Wedding:
        """
        Atualiza os dados de um casamento existente.
        """
        # O multitenancy já foi garantido pelo for_user no ViewSet,
        # então 'instance' já pertence a 'user'.

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() garante que validações de negócio do Model (ADR-009)
        # sejam respeitadas antes de salvar.
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Wedding) -> None:
        """
        Executa a deleção real (Hard Delete) do casamento.
        Como removemos o Soft Delete, o Django cuidará do CASCADE real.
        """
        # Se você definiu PROTECT em alguma relação (ex: Contratos com pagamentos),
        # o Django impedirá a deleção aqui, protegendo a integridade financeira.
        instance.delete()
