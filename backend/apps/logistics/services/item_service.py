from __future__ import annotations

import logging
from typing import TYPE_CHECKING, cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.logistics.models import Item
from apps.logistics.schemas import ItemIn, ItemPatchIn
from apps.tenants.models import Company


if TYPE_CHECKING:
    from apps.contracts.models import Contract
    from apps.weddings.models import Wedding

logger = logging.getLogger(__name__)


class ItemService:
    """Camada de serviço de aplicação para gestão e ciclo de vida de itens de logística."""

    @staticmethod
    def _resolve_wedding(
        company: Company, wedding_input: UUID | str | Wedding | None
    ) -> Wedding | None:
        """Resolve um casamento garantindo o isolamento multitenant.

        Returns:
            Instância resolvida do casamento, ou None se não fornecido.

        Raises:
            ObjectNotFoundError: Se o casamento não for encontrado para o tenant.
        """
        if not wedding_input:
            return None

        from django.apps import apps

        wedding_model = apps.get_model("weddings", "Wedding")

        return cast(
            "Wedding | None",
            resolve_tenant_resource(
                wedding_model,
                company,
                wedding_input,
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            ),
        )

    @staticmethod
    def _resolve_contract(
        company: Company, contract_input: UUID | str | Contract | None
    ) -> Contract | None:
        """Resolve um contrato garantindo o isolamento multitenant.

        Returns:
            Instância resolvida do contrato, ou None se não fornecido.

        Raises:
            ObjectNotFoundError: Se o contrato não for encontrado para o tenant.
        """
        if not contract_input:
            return None

        from django.apps import apps

        contract_model = apps.get_model("contracts", "Contract")

        return cast(
            "Contract | None",
            resolve_tenant_resource(
                contract_model,
                company,
                contract_input,
                detail="Contrato inválido ou acesso negado.",
                code="contract_not_found_or_denied",
            ),
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ItemIn) -> Item:
        """Cria um novo item de logística associado ao tenant.

        Regra de Negócio:
            BR-L04: Desacoplamento de suprimentos e pagamentos.
            ADR-030: Validação de consistência entre casamento do item e do contrato.

        Efeitos Colaterais:
            Persiste o novo item de logística na base de dados.

        Returns:
            Instância do item criada e salva no banco.

        Raises:
            DomainIntegrityError: Se o casamento do item não coincidir com o do contrato.
            BusinessRuleViolation: Se nem casamento nem contrato forem informados.
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
                if resolved_wedding:
                    wedding = resolved_wedding
        else:
            wedding = ItemService._resolve_wedding(company, wedding_input)

        # 3. Instanciação
        if wedding is None:
            raise BusinessRuleViolation(
                detail="É necessário informar um casamento ou um contrato vinculado.",
                code="item_missing_wedding",
            )

        item = Item(company=company, wedding=wedding, contract=contract, **data)
        try:
            item.save()
        except ValidationError as exc:
            if "contract" in getattr(exc, "message_dict", {}):
                raise DomainIntegrityError(
                    detail=(
                        "O wedding informado não corresponde ao wedding do contrato."
                    ),
                    code="item_contract_wedding_mismatch",
                ) from exc
            raise

        logger.info(f"Item criado com sucesso: uuid={item.uuid}")
        return item

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Item, payload: ItemPatchIn) -> Item:
        """Atualiza os dados de um item de logística existente.

        Efeitos Colaterais:
            Persiste as alterações cadastrais ou de status do item no banco.

        Returns:
            Instância atualizada do item.

        Raises:
            DomainIntegrityError: Se o novo contrato não pertencer ao casamento do item.
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

        updated_fields: set[str] = set()

        data = payload.model_dump(exclude_unset=True)

        if "contract" in data:
            contract_input = data.pop("contract")
            contract = ItemService._resolve_contract(company, contract_input)
            if contract:
                instance.assign_contract(contract)
            else:
                instance.detach_contract()
            updated_fields.add("contract")

        status_input = data.pop("acquisition_status", None)
        if status_input is not None and status_input != instance.acquisition_status:
            instance.transition_to(status_input)
            updated_fields.add("acquisition_status")

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            instance.save(update_fields=list(updated_fields))

        logger.info(f"Item uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Item) -> None:
        """Remove um item de logística do banco de dados.

        Efeitos Colaterais:
            Exclui o registro do item de logística da base de dados.

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
        """Realiza a transição do status de aquisição de um item.

        Regra de Negócio:
            BR-L04: Autômato de estados de aquisição do suprimento logístico.

        Efeitos Colaterais:
            Persiste o novo status de aquisição do item na base de dados.

        Args:
            new_status: Novo status de aquisição pretendido para o item.

        Returns:
            Instância do item com o status atualizado.

        Raises:
            BusinessRuleViolation: Se a transição de status for inválida.
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

        instance.transition_to(new_status)
        try:
            instance.save(update_fields=["acquisition_status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages),
                code="item_invalid_status_transition",
            ) from e

        logger.info(f"Item uuid={instance.uuid} transitado para '{new_status}'.")
        return instance

    @staticmethod
    @transaction.atomic
    def start(company: Company, instance: Item) -> Item:
        """Inicia a aquisição ou execução do item, transitando para EM ANDAMENTO.

        Efeitos Colaterais:
            Persiste a transição para EM ANDAMENTO na base de dados.

        Returns:
            Instância atualizada do item.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.start()
        try:
            instance.save(update_fields=["acquisition_status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="item_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def complete(company: Company, instance: Item) -> Item:
        """Conclui a aquisição do item, transitando para CONCLUÍDO.

        Efeitos Colaterais:
            Persiste a transição para CONCLUÍDO na base de dados.

        Returns:
            Instância atualizada do item.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.complete()
        try:
            instance.save(update_fields=["acquisition_status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="item_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def reopen(company: Company, instance: Item) -> Item:
        """Reabre um item concluído, transitando de volta para EM ANDAMENTO.

        Efeitos Colaterais:
            Persiste a transição para EM ANDAMENTO na base de dados.

        Returns:
            Instância atualizada do item.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.reopen()
        try:
            instance.save(update_fields=["acquisition_status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="item_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def revert_to_pending(company: Company, instance: Item) -> Item:
        """Reverte o item em andamento de volta para PENDENTE.

        Efeitos Colaterais:
            Persiste a reversão para PENDENTE na base de dados.

        Returns:
            Instância atualizada do item.

        Raises:
            BusinessRuleViolation: Se a transição for inválida.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.revert_to_pending()
        try:
            instance.save(update_fields=["acquisition_status", "updated_at"])
        except ValidationError as e:
            raise BusinessRuleViolation(
                detail="; ".join(e.messages) if hasattr(e, "messages") else str(e),
                code="item_invalid_status_transition",
            ) from e
        return instance

    @staticmethod
    @transaction.atomic
    def discard(company: Company, instance: Item, reason: str) -> Item:
        """Descarta o item do escopo registrando compulsoriamente a justificativa (RF-15).

        Regra de Negócio:
            BR-L06: Justificativa obrigatória no descarte do suprimento do escopo.

        Efeitos Colaterais:
            Atualiza o status de escopo para DESCARTADO e salva o motivo na base de dados.

        Args:
            reason: Motivo ou justificativa obrigatória para o descarte.

        Returns:
            Instância atualizada do item descartado.

        Raises:
            BusinessRuleViolation: Se o motivo de descarte for vazio.
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.discard(reason)
        instance.save(update_fields=["scope_status", "rejection_reason", "updated_at"])
        logger.info(f"Item uuid={instance.uuid} descartado com motivo: {reason}")
        return instance

    @staticmethod
    @transaction.atomic
    def include(company: Company, instance: Item) -> Item:
        """Reintegra o item ao escopo aprovado do evento.

        Efeitos Colaterais:
            Atualiza o status de escopo para INCLUÍDO e limpa o motivo de rejeição.

        Returns:
            Instância atualizada do item reintegrado.

        Raises:
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.include()
        instance.save(update_fields=["scope_status", "rejection_reason", "updated_at"])
        logger.info(f"Item uuid={instance.uuid} reintegrado ao escopo com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def deliver(company: Company, instance: Item) -> Item:
        """Registra a conferência física e entrega do material no local (RF-15).

        Efeitos Colaterais:
            Atualiza o status de entrega para ENTREGUE na base de dados.

        Returns:
            Instância atualizada do item com entrega registrada.

        Raises:
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.mark_as_delivered()
        instance.save(update_fields=["delivery_status", "updated_at"])
        logger.info(f"Item uuid={instance.uuid} marcado como entregue na portaria.")
        return instance

    @staticmethod
    @transaction.atomic
    def mark_returned(company: Company, instance: Item) -> Item:
        """Registra a devolução física do material após o evento.

        Efeitos Colaterais:
            Atualiza o status de entrega para DEVOLVIDO na base de dados.

        Returns:
            Instância atualizada do item com devolução registrada.

        Raises:
            ObjectNotFoundError: Se o item não pertencer ao tenant.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Item de logística não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
        instance.mark_as_returned()
        instance.save(update_fields=["delivery_status", "updated_at"])
        logger.info(f"Item uuid={instance.uuid} marcado como devolvido pós-evento.")
        return instance
