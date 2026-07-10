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
        """
        Lista os itens de logística pertencentes ao tenant.

        Permite filtrar os itens por casamento, status de aquisição, termo
        de busca no nome do item ou contrato associado.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_id: Identificador único (UUID ou string) do casamento.
            status: Status de aquisição do item para filtragem.
            search: Termo de busca para busca parcial no nome do item.
            contract_id: Identificador único (UUID ou string) do contrato.

        Returns:
            QuerySet contendo os itens que atendem aos filtros aplicados.
        """
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
        """
        Recupera um item de logística específico pelo UUID.

        Realiza a busca garantindo o isolamento multitenant.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: Identificador único (UUID ou string) do item.

        Returns:
            O objeto Item correspondente.

        Raises:
            ObjectNotFoundError: Se o item não for encontrado ou não pertencer
                ao tenant.
        """
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
        Resolve um casamento garantindo o isolamento multitenant.

        Aceita uma instância de Wedding, UUID ou string identificadora.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_input: Instância, UUID ou string do casamento.

        Returns:
            A instância resolvida do casamento, ou None se não fornecido.

        Raises:
            ObjectNotFoundError: Se o casamento não for encontrado para o tenant.
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
        Resolve um contrato garantindo o isolamento multitenant.

        Aceita uma instância de Contract, UUID ou string identificadora.

        Args:
            company: O tenant atual para isolamento de dados.
            contract_input: Instância, UUID ou string do contrato.

        Returns:
            A instância resolvida do contrato, ou None se não fornecido.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado para o tenant.
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
        """
        Cria um novo item de logística associado ao tenant.

        Garante que o item esteja vinculado a um casamento válido e,
        se houver contrato associado, valida a correspondência do
        casamento com o do contrato.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do item.

        Returns:
            A instância do Item criada e salva no banco.

        Raises:
            DomainIntegrityError: Se o casamento do item não coincidir
                com o casamento do contrato informado.
            BusinessRuleViolation: Se nem o casamento nem o contrato
                forem informados.
        """
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
        """
        Atualiza os dados de um item de logística existente.

        Valida a propriedade do tenant antes da alteração e garante
        que o contrato informado pertença ao mesmo casamento do item.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância atual do Item a ser atualizada.
            payload: Dados parciais para atualização do item.

        Returns:
            A instância atualizada do Item.

        Raises:
            DomainIntegrityError: Se o novo contrato informado não pertencer
                ao casamento do item.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
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
        """
        Remove um item de logística do banco de dados.

        Verifica a propriedade do tenant antes de efetuar a exclusão.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Item a ser removida.

        Raises:
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
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
        """
        Realiza a transição do status de aquisição de um item.

        Valida as regras de transição e a propriedade do tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do Item a ter o status alterado.
            new_status: O novo status desejado para o item.

        Returns:
            A instância do Item com o status atualizado.

        Raises:
            BusinessRuleViolation: Se a transição de status for inválida
                segundo as regras de validação do modelo.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
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
