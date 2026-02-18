from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.finances.models import BudgetCategory
from apps.logistics.dto import ItemDTO
from apps.logistics.models import Contract, Item


class ItemService:
    """
    Camada de serviço para gestão de itens de logística.
    Garante a integridade entre categorias de orçamento, contratos e
    casamentos (RF07/RF08).
    """

    @staticmethod
    @transaction.atomic
    def create(dto: ItemDTO) -> Item:
        """
        Cria um item garantindo a herança de contexto da categoria de orçamento pai.
        """
        # 1. Busca instâncias pai para garantir o contexto e segurança
        # (Herança de Contexto / ADR-009)
        category = BudgetCategory.objects.get(
            uuid=dto.budget_category_id, planner_id=dto.planner_id
        )

        # 2. Validação opcional de contrato (Garante que o contrato é do
        # mesmo casamento)
        contract = None
        if dto.contract_id:
            contract = Contract.objects.get(
                uuid=dto.contract_id, planner_id=dto.planner_id
            )
            if contract.wedding_id != category.wedding_id:
                raise DjangoValidationError(
                    "O contrato selecionado pertence a outro casamento."
                )

        data = dto.model_dump()

        # 3. Limpeza de IDs para evitar conflitos de argumentos no .create()
        data.pop("budget_category_id")
        data.pop("contract_id", None)
        data.pop("wedding_id", None)
        data.pop("planner_id", None)

        # 4. Criação com injeção de instâncias validadas
        return Item.objects.create(
            planner=category.planner,
            wedding=category.wedding,
            budget_category=category,
            contract=contract,
            **data,
        )

    @staticmethod
    @transaction.atomic
    def update(instance: Item, dto: ItemDTO) -> Item:
        """
        Atualiza o item protegendo campos imutáveis e validando trocas de vínculo.
        """
        # Bloqueamos a troca de Casamento, Dono ou Categoria via atualização
        exclude_fields = {"planner_id", "wedding_id", "budget_category_id"}
        data = dto.model_dump(exclude=exclude_fields)

        # Se houver troca de contrato, validamos se ele pertence ao mesmo contexto
        if dto.contract_id and str(dto.contract_id) != str(instance.contract_id):
            contract = Contract.objects.get(
                uuid=dto.contract_id, planner_id=instance.planner_id
            )
            if contract.wedding_id != instance.wedding_id:
                raise DjangoValidationError(
                    "O contrato selecionado pertence a outro casamento."
                )
            instance.contract = contract
        elif dto.contract_id is None:
            instance.contract = None

        # Atualização dinâmica de campos
        for field, value in data.items():
            if field != "contract_id":  # Já tratado acima
                setattr(instance, field, value)

        instance.save()  # Dispara full_clean() -> Valida RF07.1
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Item) -> None:
        """
        Executa a deleção lógica do item (ADR-008).
        """
        # Conforme ADR-008, a deleção é lógica para preservar o histórico de
        # planejamento.
        instance.delete()
