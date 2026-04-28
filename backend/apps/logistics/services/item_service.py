import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import DomainIntegrityError
from apps.core.types import AuthContextUser
from apps.logistics.models import Contract, Item
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class ItemService:
    """
    Camada de serviço para orquestração de Itens/Serviços.
    Focada em mutações e isolamento de dados.
    """

    @staticmethod
    def list(
        user: AuthContextUser, wedding_id: UUID | str | None = None
    ) -> QuerySet[Item]:
        qs = Item.objects.for_user(user).select_related("contract", "wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Item:
        return Item.objects.resolve(user, uuid)

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Item:
        logger.info("Iniciando criação de Item")

        # 1. Resolução do Casamento
        wedding_input = data.pop("wedding")
        wedding = Wedding.objects.resolve(user, wedding_input)

        # 2. Resolução do Contrato (Opcional)
        contract = None
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                contract = Contract.objects.resolve(user, contract_input)
                # Garantia de integridade: contrato deve pertencer ao mesmo wedding
                if contract.wedding_id != wedding.id:
                    from apps.core.exceptions import BusinessRuleViolation

                    raise BusinessRuleViolation(
                        detail="Este contrato pertence a outro casamento.",
                        code="invalid_contract_wedding",
                    )

        # 3. Instanciação e Persistência
        item = Item(wedding=wedding, contract=contract, **data)
        item.save()

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(user: AuthContextUser, instance: Item, data: dict[str, Any]) -> Item:
        logger.info(f"Atualizando Item uuid={instance.uuid}")

        # Bloqueio de troca de casamento
        data.pop("wedding", None)

        # Tratamento de troca de contrato
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                contract = Contract.objects.resolve(user, contract_input)
                if contract.wedding_id != instance.wedding_id:
                    from apps.core.exceptions import BusinessRuleViolation

                    raise BusinessRuleViolation(
                        detail="Este contrato pertence a outro casamento.",
                        code="invalid_contract_wedding",
                    )
                instance.contract = contract
            else:
                instance.contract = None

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Item) -> None:
        logger.info("Deletando Item uuid=%s", instance.uuid)

        try:
            instance.delete()
        except ProtectedError as e:
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar este item pois existem "
                    "registros dependentes."
                ),
                code="item_protected_error",
            ) from e
