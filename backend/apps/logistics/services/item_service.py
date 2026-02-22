import logging

from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import BudgetCategory
from apps.logistics.models import Contract, Item


logger = logging.getLogger(__name__)


class ItemService:
    """
    Camada de serviço para gestão de itens de logística.
    Garante a integridade entre categorias de orçamento, contratos e casamentos.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Item:
        logger.info(f"Iniciando criação de Item logístico para planner_id={user.id}")

        # 1. Resolução Segura de Dependências (Suporta Instância ou UUID do DRF)
        category_input = data.pop("budget_category", None)

        if isinstance(category_input, BudgetCategory):
            category = category_input
        else:
            try:
                category = (
                    BudgetCategory.objects.all().for_user(user).get(uuid=category_input)
                )
            except BudgetCategory.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de categoria inválida/negada: {category_input}"
                )
                raise BusinessRuleViolation(
                    detail="Categoria de orçamento não encontrada ou acesso negado.",
                    code="budget_category_not_found_or_denied",
                ) from e

        # 2. Tratamento opcional de contrato
        contract = None
        contract_input = data.pop("contract", None)

        if contract_input:
            if isinstance(contract_input, Contract):
                contract = contract_input
            else:
                try:
                    contract = (
                        Contract.objects.all().for_user(user).get(uuid=contract_input)
                    )
                except Contract.DoesNotExist as e:
                    logger.warning(
                        f"Tentativa de uso de contrato inválido/negado: "
                        f"{contract_input}"
                    )
                    raise BusinessRuleViolation(
                        detail="Contrato não encontrado ou acesso negado.",
                        code="contract_not_found_or_denied",
                    ) from e

        # 3. Injeção automática de contexto e Instanciação
        item = Item(
            planner=user,
            wedding=category.wedding,
            budget_category=category,
            contract=contract,
            **data,
        )

        # 4. Validação de consistência (Model assume o controle)
        item.full_clean()
        item.save()

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(instance: Item, user, data: dict) -> Item:
        logger.info(f"Atualizando Item uuid={instance.uuid} por planner_id={user.id}")

        # Bloqueio de troca de contexto base
        data.pop("planner", None)
        data.pop("wedding", None)
        data.pop("budget_category", None)

        # Tratamento de troca de contrato (com suporte a null/desvinculação)
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                if isinstance(contract_input, Contract):
                    instance.contract = contract_input
                else:
                    try:
                        instance.contract = (
                            Contract.objects.all()
                            .for_user(user)
                            .get(uuid=contract_input)
                        )
                    except Contract.DoesNotExist as e:
                        raise BusinessRuleViolation(
                            detail="Contrato inválido ou acesso negado.",
                            code="contract_not_found_or_denied",
                        ) from e
            else:
                instance.contract = None

        # Atualização dos campos restantes
        for field, value in data.items():
            setattr(instance, field, value)

        # Validação final de consistência (Cross-Wedding check no Mixin)
        instance.full_clean()
        instance.save()

        logger.info(f"Item uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Item) -> None:
        logger.info(
            f"Tentativa de deleção do Item uuid={instance.uuid} por "
            f"planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Item uuid={instance.uuid} DESTRUÍDO por planner_id={user.id}"
            )

        except ProtectedError as e:
            logger.error(f"Falha de integridade ao deletar Item uuid={instance.uuid}")
            raise DomainIntegrityError(
                detail="Não é possível apagar este item pois existem registros "
                "dependentes vinculados a ele.",
                code="item_protected_error",
            ) from e
