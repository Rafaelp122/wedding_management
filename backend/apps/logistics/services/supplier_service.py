from django.db import transaction

from apps.logistics.models import Supplier


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de catálogo transversal ao Planner (RF09).
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Supplier:
        """
        Cria um novo fornecedor vinculado ao Planner autenticado.
        """
        # Injeção de posse direta do contexto de autenticação.
        data["planner"] = user

        # Como o fornecedor é PlannerOwned (transversal), não precisa de wedding_id.
        return Supplier.objects.create(**data)

    @staticmethod
    @transaction.atomic
    def update(instance: Supplier, user, data: dict) -> Supplier:
        """
        Atualiza os dados de um fornecedor protegendo a imutabilidade do dono.
        """
        # Impedimos que o fornecedor mude de dono via API.
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() aqui é vital caso existam validações de CNPJ único por Planner,
        # ou outros campos obrigatórios de negócio.
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Supplier) -> None:
        """
        Executa a deleção real do fornecedor.
        A integridade com contratos existentes é garantida pelo banco de dados.
        """
        # Se você definiu on_delete=models.PROTECT no modelo Contract,
        # o Django impedirá a deleção se houver contratos ativos, disparando um erro.
        instance.delete()
