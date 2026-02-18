from django.db import transaction

from apps.logistics.dto import SupplierDTO
from apps.logistics.models import Supplier


class SupplierService:
    """
    Camada de serviço para gestão de fornecedores.
    Centraliza a lógica de criação, atualização e deleção (RF09).
    """

    @staticmethod
    @transaction.atomic
    def create(dto: SupplierDTO) -> Supplier:
        """
        Cria um novo fornecedor garantindo a correta atribuição ao Planner.
        """
        # 1. Preparação dos dados e extração de contexto
        # (Segurança e Integridade)
        data = dto.model_dump()
        planner_id = data.pop("planner_id")

        # 2. Criação com injeção de contexto validado
        return Supplier.objects.create(planner_id=planner_id, **data)

    @staticmethod
    @transaction.atomic
    def update(instance: Supplier, dto: SupplierDTO) -> Supplier:
        """
        Atualiza um fornecedor existente protegendo a imutabilidade do dono.
        """
        # Bloqueamos a troca de Dono via atualização (ADR-009)
        exclude_fields = {"planner_id"}
        data = dto.model_dump(exclude=exclude_fields)

        # Atualização dinâmica de campos
        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Supplier) -> None:
        """
        Executa a deleção lógica do fornecedor (ADR-008).
        """
        # Conforme ADR-008, a deleção é lógica para preservar histórico e
        # integridade de contratos passados.
        instance.delete()
