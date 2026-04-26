import logging
from typing import Any

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.core.types import AuthContextUser

from ..models import Wedding


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
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Wedding:
        planner = require_user(user)
        logger.info("Criando casamento para planner_id=%s", planner.id)

        # Proteção defensiva: remove campos de sistema que não devem vir via payload
        data.pop("planner", None)
        data.pop("planner_id", None)
        data.pop("uuid", None)

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        model_data = {k: v for k, v in data.items() if k in valid_fields}

        # Instanciação e Validação do Casamento
        wedding = Wedding(planner=planner, **model_data)

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
                detail=detail, code="wedding_validation_error"
            ) from e

        logger.info("Casamento criado com sucesso: uuid=%s", wedding.uuid)
        return wedding

    @staticmethod
    @transaction.atomic
    def update(instance: Wedding, data: dict[str, Any]) -> Wedding:
        """Atualiza uma instância de casamento com novos dados."""
        logger.info("Atualizando casamento uuid=%s", instance.uuid)

        # Proteção defensiva: impede troca de dono ou ID via update genérico
        data.pop("planner", None)
        data.pop("planner_id", None)
        data.pop("uuid", None)

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        for field, value in data.items():
            if field in valid_fields:
                setattr(instance, field, value)

        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                "Falha de validação ao atualizar casamento uuid=%s: %s",
                instance.uuid,
                e,
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail, code="wedding_validation_error"
            ) from e

        logger.info("Casamento uuid=%s atualizado.", instance.uuid)
        return instance

    @staticmethod
    @transaction.atomic
    def delete(instance: Wedding) -> None:
        """Deleta uma instância de casamento."""
        logger.info("Tentativa de deleção do casamento uuid=%s", instance.uuid)

        try:
            instance.delete()
            logger.warning("Casamento uuid=%s e dependências removidos.", instance.uuid)
        except ProtectedError as e:
            logger.error(
                "Falha de integridade: Casamento uuid=%s protegido.", instance.uuid
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este casamento pois existem contratos ou "
                "despesas vinculadas a ele.",
                code="wedding_protected_error",
            ) from e
