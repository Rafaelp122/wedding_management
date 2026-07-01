from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.logistics.models import Contract, Item
from apps.logistics.schemas import ItemIn, ItemPatchIn
from apps.tenants.models import Company


if TYPE_CHECKING:
    from apps.weddings.models import Wedding

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
        return get_object_or_404_for_tenant(
            Item,
            company,
            uuid,
            select_related=["wedding", "contract", "contract__supplier"],
            detail="Item de logística não encontrado.",
        )

    @staticmethod
    def _resolve_wedding(
        company: Company, wedding_input: UUID | str | Wedding | None
    ) -> Wedding | None:
        """
        Resolve um casamento (instância, UUID ou string) garantindo multi-tenancy.
        """
        if not wedding_input:
            return None

        from django.apps import apps

        Wedding = apps.get_model("weddings", "Wedding")

        if isinstance(wedding_input, Wedding):
            return wedding_input
        if isinstance(wedding_input, UUID | str):
            return get_object_or_404_for_tenant(
                Wedding,
                company,
                wedding_input,
                code="wedding_not_found_or_denied",
            )
        return None

    @staticmethod
    def _resolve_contract(
        company: Company, contract_input: UUID | str | Contract | None
    ) -> Contract | None:
        """
        Resolve um contrato (instância, UUID ou string) garantindo multi-tenancy.
        """
        if not contract_input:
            return None

        if isinstance(contract_input, Contract):
            return contract_input

        return get_object_or_404_for_tenant(
            Contract,
            company,
            contract_input,
            code="contract_not_found_or_denied",
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ItemIn) -> Item:
        logger.info(f"Iniciando criação de Item para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)

        # 2. Tratamento de contrato
        contract_input = data.pop("contract", None)
        contract = ItemService._resolve_contract(company, contract_input)

        wedding: Wedding | None = None
        if contract:
            wedding = contract.wedding
            if wedding_input:
                resolved_wedding = ItemService._resolve_wedding(company, wedding_input)
                if resolved_wedding and wedding != resolved_wedding:
                    raise DomainIntegrityError(
                        detail=(
                            "O wedding informado não corresponde ao wedding "
                            "do contrato."
                        ),
                        code="item_contract_wedding_mismatch",
                    )
        else:
            wedding = ItemService._resolve_wedding(company, wedding_input)

        # 3. Instanciação
        if wedding is None:
            raise BusinessRuleViolation(
                detail="É necessário informar um casamento ou um contrato vinculado.",
                code="item_missing_wedding",
            )

        item = Item(company=company, wedding=wedding, contract=contract, **data)
        item.save()

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Item, payload: ItemPatchIn) -> Item:
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Item uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        if "contract" in data:
            contract_input = data.pop("contract")
            contract = ItemService._resolve_contract(company, contract_input)
            if contract and contract.wedding != instance.wedding:
                raise DomainIntegrityError(
                    detail="O contrato informado não pertence ao casamento deste item.",
                    code="item_contract_wedding_mismatch",
                )
            instance.contract = contract

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        logger.info(f"Item uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Item) -> None:
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
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
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        logger.info(
            f"Transição de status do Item uuid={instance.uuid}: "
            f"{instance.acquisition_status} -> {new_status}"
        )

        instance.acquisition_status = new_status
        try:
            instance.save()
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages),
                code="item_invalid_status_transition",
            ) from e

        logger.info(f"Item uuid={instance.uuid} transitado para '{new_status}'.")
        return instance
