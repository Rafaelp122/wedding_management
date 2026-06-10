import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    ObjectNotFoundError,
)
from apps.logistics.models import Contract, Item
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class ItemService:
    """
    Camada de serviço para gestão de itens de logística.
    Garante a integridade entre contratos e casamentos.
    """

    @staticmethod
    def list(
        company: Company,
        wedding_id: UUID | str | None = None,
        status: str | None = None,
        search: str | None = None,
        contract_id: UUID | str | None = None,
    ) -> QuerySet[Item]:
        qs = Item.objects.for_tenant(company).select_related(
            "wedding", "contract", "contract__supplier"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        if status:
            qs = qs.filter(acquisition_status=status)
        if search:
            qs = qs.filter(name__icontains=search)
        if contract_id:
            qs = qs.filter(contract__uuid=contract_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Item:
        try:
            return (
                Item.objects.for_tenant(company)
                .select_related("wedding", "contract", "contract__supplier")
                .get(uuid=uuid)
            )
        except Item.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Item de logística não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Item:
        logger.info(f"Iniciando criação de Item logístico para company_id={company.id}")

        # 1. Resolução do Casamento (Item é WeddingOwnedMixin)
        wedding_input = data.pop("wedding", None)
        wedding = None

        # 2. Tratamento de contrato
        contract = None
        contract_input = data.pop("contract", None)

        if contract_input:
            if isinstance(contract_input, Contract):
                contract = contract_input
                wedding = contract.wedding
            else:
                try:
                    contract = Contract.objects.for_tenant(company).get(
                        uuid=contract_input
                    )
                    wedding = contract.wedding
                except Contract.DoesNotExist as e:
                    logger.warning(
                        f"Tentativa de uso de contrato inválido/negado: "
                        f"{contract_input}"
                    )
                    raise ObjectNotFoundError(
                        detail="Contrato não encontrado ou acesso negado.",
                        code="contract_not_found_or_denied",
                    ) from e
        elif isinstance(wedding_input, UUID | str) or isinstance(wedding_input, str):
            from apps.weddings.models import Wedding

            try:
                wedding = Wedding.objects.for_tenant(company).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 3. Instanciação
        item = Item(company=company, wedding=wedding, contract=contract, **data)

        item.save()

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Item, data: dict[str, Any]) -> Item:
        logger.info(
            f"Atualizando Item uuid={instance.uuid} por company_id={company.id}"
        )

        data.pop("company", None)
        data.pop("wedding", None)

        if "contract" in data:
            contract_input = data.pop("contract")
            if contract_input:
                if isinstance(contract_input, Contract):
                    instance.contract = contract_input
                else:
                    try:
                        instance.contract = Contract.objects.for_tenant(company).get(
                            uuid=contract_input
                        )
                    except Contract.DoesNotExist as e:
                        raise ObjectNotFoundError(
                            detail="Contrato inválido ou acesso negado.",
                            code="contract_not_found_or_denied",
                        ) from e
            else:
                instance.contract = None

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Item uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Item) -> None:
        logger.info(
            f"Tentativa de deleção do Item uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        instance.delete()
        logger.warning(
            f"Item uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
        )

    @staticmethod
    @transaction.atomic
    def transition_status(company: Company, instance: Item, new_status: str) -> Item:
        logger.info(
            f"Transição de status do Item uuid={instance.uuid}: "
            f"{instance.acquisition_status} -> {new_status}"
        )

        # TODO(sprint/018): mover máquina de estados para Item.clean()
        allowed_transitions: dict[str, list[str]] = {
            "PENDING": ["IN_PROGRESS"],
            "IN_PROGRESS": ["DONE", "PENDING"],
            "DONE": ["IN_PROGRESS"],
        }

        current = instance.acquisition_status
        allowed = allowed_transitions.get(current, [])

        if new_status not in allowed:
            raise BusinessRuleViolation(
                detail=f"Não é permitido transitar de '{current}' para '{new_status}'.",
                code="item_invalid_status_transition",
            )

        instance.acquisition_status = new_status
        instance.save()

        logger.info(f"Item uuid={instance.uuid} transitado para '{new_status}'.")
        return instance
