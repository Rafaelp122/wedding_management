from django.core.exceptions import ValidationError
from django.db import transaction

from apps.finances.models import BudgetCategory
from apps.logistics.models import Contract, Item


class ItemService:
    """
    Camada de serviço para gestão de itens de logística.
    Garante a integridade entre categorias de orçamento, contratos e casamentos.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Item:
        """
        Cria um item garantindo a herança de contexto da categoria de orçamento.
        """
        # 1. Recuperamos a categoria garantindo que ela pertence ao Planner
        category_uuid = data.pop("budget_category", None)
        try:
            category = (
                BudgetCategory.objects.all().for_user(user).get(uuid=category_uuid)
            )
        except BudgetCategory.DoesNotExist:
            raise ValidationError({
                "budget_category": "Categoria não encontrada ou acesso negado."
            }) from BudgetCategory.DoesNotExist

        # 2. Tratamento opcional de contrato
        contract = None
        contract_uuid = data.pop("contract", None)
        if contract_uuid:
            try:
                contract = Contract.objects.all().for_user(user).get(uuid=contract_uuid)
            except Contract.DoesNotExist:
                raise ValidationError({
                    "contract": "Contrato não encontrado ou acesso negado."
                }) from Contract.DoesNotExist

        # 3. Injeção automática de contexto (Multitenancy ADR-009)
        # O item herda o casamento da categoria pai.
        data["planner"] = user
        data["wedding"] = category.wedding
        data["budget_category"] = category
        data["contract"] = contract

        # 4. Criação e validação de consistência
        item = Item(**data)
        # O full_clean() disparará o WeddingOwnedMixin para garantir que
        # o contrato pertence ao mesmo casamento da categoria.
        item.full_clean()
        item.save()
        return item

    @staticmethod
    @transaction.atomic
    def update(instance: Item, user, data: dict) -> Item:
        """
        Atualiza o item protegendo vínculos de propriedade.
        """
        # Bloqueamos a troca de Casamento, Dono ou Categoria pai
        data.pop("planner", None)
        data.pop("wedding", None)
        data.pop("budget_category", None)

        # Tratamento de troca de contrato
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

        # Atualização dos campos restantes (name, quantity, status, etc)
        for field, value in data.items():
            setattr(instance, field, value)

        # Validação final de consistência (Cross-Wedding check no Mixin)
        instance.full_clean()
        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Item) -> None:
        """
        Executa a deleção real (Hard Delete).
        """
        # Sem Soft Delete, a deleção é definitiva.
        instance.delete()
