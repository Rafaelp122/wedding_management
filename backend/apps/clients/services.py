"""
Serviços de mutação para o domínio de clientes (CQRS).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError

from apps.clients.models import Client
from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.tenant import validate_tenant_ownership


if TYPE_CHECKING:
    from apps.clients.schemas import ClientIn, ClientPatchIn
    from apps.tenants.models import Company

logger = logging.getLogger(__name__)


class ClientService:
    """Serviço de aplicação para mutações do ciclo de vida de clientes."""

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: ClientIn) -> Client:
        """Cria e persiste um novo cliente associado ao tenant.

        Efeitos Colaterais:
            Persiste o novo registro de cliente na base de dados.

        Returns:
            Instância do cliente criada e persistida.

        Raises:
            BusinessRuleViolation: Se houver violação de validação nos dados informados.
        """
        logger.info(f"Criando cliente para company_id={company.id}")
        client = Client(
            company=company,
            name=payload.name,
            cpf=payload.cpf,
            email=payload.email,
            phone=payload.phone,
            notes=payload.notes,
        )
        try:
            client.save()
        except DjangoValidationError as exc:
            logger.warning(
                "Erro de validação ao criar cliente para company_id=%s: %s",
                company.id,
                exc,
            )
            detail = "; ".join(exc.messages) if exc.messages else str(exc)
            raise BusinessRuleViolation(
                detail=detail,
                code="client_validation_error",
            ) from exc

        return client

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Client, payload: ClientPatchIn) -> Client:
        """Atualiza os dados cadastrais de um cliente existente do tenant.

        Efeitos Colaterais:
            Persiste as alterações cadastrais do cliente no banco de dados.

        Returns:
            Instância do cliente atualizada.

        Raises:
            BusinessRuleViolation: Se os dados violarem regras de validação ou o tenant for incompatível.
        """
        validate_tenant_ownership(company, instance)

        instance.update_contact_info(
            name=payload.name,
            cpf=payload.cpf,
            email=payload.email,
            phone=payload.phone,
            notes=payload.notes,
        )
        try:
            instance.save()
        except DjangoValidationError as exc:
            logger.warning(
                f"Erro de validação ao atualizar cliente uuid={instance.uuid}: {exc}"
            )
            detail = "; ".join(exc.messages) if exc.messages else str(exc)
            raise BusinessRuleViolation(
                detail=detail,
                code="client_validation_error",
            ) from exc

        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Client) -> None:
        """Remove com segurança um cliente pertencente ao tenant.

        Efeitos Colaterais:
            Exclui o registro de cliente da base de dados.

        Raises:
            DomainIntegrityError: Se o cliente estiver protegido por vínculos ativos com casamentos.
            BusinessRuleViolation: Se o cliente pertencer a outro tenant.
        """
        validate_tenant_ownership(company, instance)

        try:
            instance.delete()
            logger.info(
                "Cliente uuid=%s removido com sucesso pela company_id=%s",
                instance.uuid,
                company.id,
            )
        except ProtectedError as exc:
            logger.exception(
                "Falha de integridade: Cliente uuid=%s protegido por vínculos.",
                instance.uuid,
            )
            raise DomainIntegrityError(
                detail="Não é possível excluir este cliente pois ele está vinculado "
                "como participante em casamentos.",
                code="client_protected_error",
            ) from exc
