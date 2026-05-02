import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.tenants.models import Company

from ..models import Wedding


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.

    Nota: Budget e suas categorias são criados sob demanda (lazy loading)
    através do BudgetService.get_or_create_for_wedding().
    """

    @staticmethod
    def list(company: Company) -> QuerySet[Wedding]:
        return Wedding.objects.for_tenant(company)

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Wedding:
        wedding = Wedding.objects.for_tenant(company).filter(uuid=uuid).first()
        if wedding is None:
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )
        return wedding

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Wedding:
        logger.info(f"Criando casamento para company_id={company.id}")

        # Filtra apenas os campos que pertencem ao modelo Wedding
        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        model_data = {k: v for k, v in data.items() if k in valid_fields}

        # Instanciação e Validação do Casamento
        wedding = Wedding(company=company, **model_data)
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao criar casamento para company_id=%s: %s",
                company.id,
                e,
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        logger.info(f"Casamento criado com sucesso: uuid={wedding.uuid}")
        return wedding

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Wedding, data: dict[str, Any]) -> Wedding:
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} pela company_id={company.id}"
        )

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        for field, value in data.items():
            if field in valid_fields:
                setattr(instance, field, value)

        # Validação estrita
        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao atualizar casamento uuid=%s pela "
                "company_id=%s: %s",
                instance.uuid,
                company.id,
                e,
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        logger.info(f"Casamento uuid={instance.uuid} atualizado.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, uuid: UUID | str) -> None:
        """
        Deleta um casamento.
        """
        instance = WeddingService.get(company, uuid)
        logger.info(
            f"Tentativa de deleção do casamento uuid={instance.uuid} pela "
            f"company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Casamento uuid={instance.uuid} e dependências removidos pela "
                f"company_id={company.id}"
            )

        except ProtectedError as e:
            logger.error(
                f"Falha de integridade: Casamento uuid={instance.uuid} protegido por "
                f"contratos/despesas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este casamento pois existem contratos ou "
                "despesas vinculadas a ele.",
                code="wedding_protected_error",
            ) from e
