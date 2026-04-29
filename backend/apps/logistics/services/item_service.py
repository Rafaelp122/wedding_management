import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import DomainIntegrityError
from apps.events.models import Event
from apps.logistics.models import Contract, Item
from apps.users.types import AuthContextUser


logger = logging.getLogger(__name__)


class ItemService:
    """
    Camada de serviço para orquestração de Itens/Serviços.
    Focada em mutações e isolamento de dados.
    """

    @staticmethod
    def list(
        user: AuthContextUser, event_id: UUID | str | None = None
    ) -> QuerySet[Item]:
        qs = Item.objects.for_user(user).select_related("contract", "event")
        if event_id:
            qs = qs.filter(event__uuid=event_id)
        return qs

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Item:
        return Item.objects.resolve(user, uuid)

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Item:
        logger.info("Iniciando criação de Item")

        # 1. Resolução do Casamento
        event_input = data.pop("event")
        event = Event.objects.resolve(user, event_input)

        # 2. Resolução do Contrato (Opcional)
        contract = None
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                contract = Contract.objects.resolve(user, contract_input)
                # Garantia de integridade: contrato deve pertencer ao mesmo event
                if contract.event_id != event.id:
                    from apps.core.exceptions import BusinessRuleViolation

                    raise BusinessRuleViolation(
                        detail="Este contrato pertence a outro casamento.",
                        code="invalid_contract_event",
                    )

        # 3. Instanciação e Persistência
        item = Item(event=event, contract=contract, **data)
        item.save()

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(user: AuthContextUser, instance: Item, data: dict[str, Any]) -> Item:
        logger.info(f"Atualizando Item uuid={instance.uuid}")

        # Bloqueio de troca de casamento
        data.pop("event", None)

        # Tratamento de troca de contrato
        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                contract = Contract.objects.resolve(user, contract_input)
                if contract.event_id != instance.event_id:
                    from apps.core.exceptions import BusinessRuleViolation

                    raise BusinessRuleViolation(
                        detail="Este contrato pertence a outro casamento.",
                        code="invalid_contract_event",
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
