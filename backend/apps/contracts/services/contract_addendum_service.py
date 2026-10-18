"""
Serviço de domínio para orquestração de Termos Aditivos de Contratos (ContractAddendum).

Responsabilidade: Mutação atômica, validação de posse multitenant, integração síncrona
com o domínio de Finanças e despacho de eventos de domínio pós-commit (RFC-001, ADR-030, ADR-031).
"""

from __future__ import annotations

import logging
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.contracts.models import Contract, ContractAddendum
from apps.contracts.schemas.contract_addendum import (
    ContractAddendumIn,
    ContractAddendumSignIn,
)
from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.finances.interfaces import add_expense_adjustment_from_addendum
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class ContractAddendumService:
    """Camada de serviço para gestão e orquestração de Termos Aditivos."""

    @staticmethod
    @transaction.atomic
    def create(
        company: Company,
        contract_id: UUID | str,
        payload: ContractAddendumIn,
    ) -> ContractAddendum:
        """Cria um novo termo aditivo vinculado ao contrato especificado.

        Regra de Negócio: [BR-L02-A](docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
        Efeitos Colaterais: Persiste a instância de ContractAddendum com status PENDING no banco de dados.
        Raises:
            BusinessRuleViolation: Se ocorrer falha de validação de modelo ao salvar.
        """
        contract = resolve_tenant_resource(
            Contract,
            company,
            contract_id,
            detail="Contrato inválido ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        addendum = ContractAddendum(
            company=company,
            wedding=contract.wedding,
            contract=contract,
            amount=payload.amount,
            justification=payload.justification,
            signed_date=payload.signed_date,
            pdf_file=payload.pdf_file_key,
            status=ContractAddendum.StatusChoices.PENDING,
        )

        try:
            addendum.save()
        except ValidationError as e:
            detail = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="addendum_validation_error",
            ) from e

        logger.info(
            "Termo aditivo uuid=%s criado para o contrato uuid=%s (empresa %s)",
            addendum.uuid,
            contract.uuid,
            company.id,
        )
        return addendum

    @staticmethod
    @transaction.atomic
    def sign(
        company: Company,
        contract_id: UUID | str,
        addendum_id: UUID | str,
        payload: ContractAddendumSignIn | None = None,
    ) -> ContractAddendum:
        """Formaliza a assinatura de um termo aditivo e atualiza finanças.

        Regra de Negócio: [BR-L02-A](docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
        Efeitos Colaterais: Altera status para SIGNED, registra ajuste financeiro e agenda task pós-commit.
        Raises:
            DomainIntegrityError: Se o aditivo não pertencer ao contrato especificado.
            BusinessRuleViolation: Se ocorrer falha ao validar ou salvar o aditivo.
        """
        contract = resolve_tenant_resource(
            Contract,
            company,
            contract_id,
            detail="Contrato inválido ou acesso negado.",
            code="contract_not_found_or_denied",
        )

        addendum = resolve_tenant_resource(
            ContractAddendum,
            company,
            addendum_id,
            detail="Termo aditivo não encontrado ou acesso negado.",
            code="contract_addendum_not_found_or_denied",
        )

        if addendum.contract_id != contract.id:
            raise DomainIntegrityError(
                detail=(
                    f"O termo aditivo informado não pertence ao contrato especificado; "
                    f"aditivo '{addendum.uuid}' vinculado ao contrato '{addendum.contract_id}' "
                    f"vs contrato informado '{contract.id}'."
                ),
                code="addendum_contract_mismatch",
            )

        signed_date = payload.signed_date if payload else None
        addendum.sign(signed_date=signed_date)

        try:
            addendum.save()
        except ValidationError as e:
            detail = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="addendum_sign_validation_error",
            ) from e

        # 1. Integração síncrona com o domínio de Finanças (ADR-031)
        add_expense_adjustment_from_addendum(
            company=company,
            contract_uuid=contract.uuid,
            addendum_amount=addendum.amount,
        )

        # 2. Despacho reativo e assíncrono pós-commit (EDA / RFC-001 / ADR-017)
        from apps.contracts.tasks import on_contract_addendum_signed_task

        transaction.on_commit(
            lambda: on_contract_addendum_signed_task.enqueue(
                company.id,
                str(contract.uuid),
                str(addendum.uuid),
                str(addendum.amount),
            )
        )

        logger.info(
            "Termo aditivo uuid=%s assinado com sucesso para contrato uuid=%s (valor: %s)",
            addendum.uuid,
            contract.uuid,
            addendum.amount,
        )
        return addendum

    @staticmethod
    @transaction.atomic
    def cancel(
        company: Company,
        contract_id: UUID | str,
        addendum_id: UUID | str,
    ) -> ContractAddendum:
        """Cancela um termo aditivo previamente registrado.

        Regra de Negócio: [BR-L02-A](docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
        Efeitos Colaterais: Altera e persiste o status do termo aditivo para CANCELED.
        Raises:
            DomainIntegrityError: Se o aditivo não pertencer ao contrato especificado.
            BusinessRuleViolation: Se ocorrer falha de validação de modelo ao cancelar.
        """
        contract = resolve_tenant_resource(
            Contract,
            company,
            contract_id,
            detail="Contrato inválido ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        addendum = resolve_tenant_resource(
            ContractAddendum,
            company,
            addendum_id,
            detail="Termo aditivo não encontrado ou acesso negado.",
            code="contract_addendum_not_found_or_denied",
        )
        if addendum.contract_id != contract.id:
            raise DomainIntegrityError(
                detail=(
                    f"O termo aditivo informado não pertence ao contrato especificado; "
                    f"aditivo '{addendum.uuid}' vinculado ao contrato '{addendum.contract_id}' "
                    f"vs contrato informado '{contract.id}'."
                ),
                code="addendum_contract_mismatch",
            )
        addendum.cancel()
        try:
            addendum.save()
        except ValidationError as e:
            detail = "; ".join(e.messages) if hasattr(e, "messages") else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="addendum_cancel_validation_error",
            ) from e
        return addendum

    @staticmethod
    @transaction.atomic
    def delete(
        company: Company,
        contract_id: UUID | str,
        addendum_id: UUID | str,
    ) -> None:
        """Exclui um termo aditivo pendente do banco de dados.

        Regra de Negócio: [BR-L02-D](docs/architecture/business-rules/logistics/contract-parent-child-hierarchy.md)
        Efeitos Colaterais: Remove permanentemente o termo aditivo do banco de dados.
        Raises:
            DomainIntegrityError: Se o aditivo não pertencer ao contrato informado.
            BusinessRuleViolation: Se tentar excluir um aditivo já assinado.
        """
        contract = resolve_tenant_resource(
            Contract,
            company,
            contract_id,
            detail="Contrato inválido ou acesso negado.",
            code="contract_not_found_or_denied",
        )
        addendum = resolve_tenant_resource(
            ContractAddendum,
            company,
            addendum_id,
            detail="Termo aditivo não encontrado ou acesso negado.",
            code="contract_addendum_not_found_or_denied",
        )
        if addendum.contract_id != contract.id:
            raise DomainIntegrityError(
                detail=(
                    f"O termo aditivo informado não pertence ao contrato especificado; "
                    f"aditivo '{addendum.uuid}' vinculado ao contrato '{addendum.contract_id}' "
                    f"vs contrato informado '{contract.id}'."
                ),
                code="addendum_contract_mismatch",
            )
        if addendum.status == ContractAddendum.StatusChoices.SIGNED:
            raise BusinessRuleViolation(
                detail=f"Não é possível excluir um termo aditivo já assinado (status atual: '{addendum.status}').",
                code="cannot_delete_signed_addendum",
            )
        addendum.delete()
