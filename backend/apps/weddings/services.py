import logging
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser

from .models import Wedding


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.

    Nota: Budget e suas categorias são criados sob demanda (lazy loading)
    através do BudgetService.get_or_create_for_wedding().
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Wedding]:
        return Wedding.objects.for_user(user)

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Wedding:
        wedding = Wedding.objects.for_user(user).filter(uuid=uuid).first()
        if wedding is None:
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )
        return wedding

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Wedding:
        planner = require_user(user)
        logger.info(f"Criando casamento para planner_id={planner.id}")

        # Limpeza: Remove campos que não pertencem ao modelo Wedding
        data.pop("total_estimated", None)

        # Instanciação e Validação do Casamento
        wedding = Wedding(planner=planner, **data)
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao criar casamento para planner_id=%s: %s",
                planner.id,
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
    def update(
        user: AuthContextUser, instance: Wedding, data: dict[str, Any]
    ) -> Wedding:
        planner = require_user(user)
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} por planner_id={planner.id}"
        )

        # Defesa contra campos financeiros que não pertencem ao Wedding
        data.pop("total_estimated", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Validação estrita (regras de negócio do Model)
        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao atualizar casamento uuid=%s por "
                "planner_id=%s: %s",
                instance.uuid,
                planner.id,
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
    def partial_update(
        user: AuthContextUser, uuid: UUID | str, data: dict[str, Any]
    ) -> Wedding:
        """
        Atualização parcial de um casamento.
        Busca a instância internamente antes de atualizar.
        """
        instance = WeddingService.get(user, uuid)
        return WeddingService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, uuid: UUID | str) -> None:
        """
        Deleta um casamento.
        Busca a instância internamente antes de deletar.
        """
        instance = WeddingService.get(user, uuid)
        planner = require_user(user)
        logger.info(
            f"Tentativa de deleção do casamento uuid={instance.uuid} por "
            f"planner_id={planner.id}"
        )

        try:
            # O Django cuidará do CASCADE para o Budget e Categorias,
            # a menos que haja PROTECT em contratos/despesas.
            instance.delete()
            logger.warning(
                f"Casamento uuid={instance.uuid} e dependências removidos por "
                f"planner_id={planner.id}"
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
