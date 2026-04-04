import logging
from typing import Any
from uuid import UUID

from django.contrib.auth.models import AnonymousUser
from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.users.models import User

from .models import Wedding


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.
    Orquestra a criação atómica do ecossistema inicial (Wedding + Budget + Categories).
    """

    @staticmethod
    def _require_user(user: AuthContextUser) -> User:
        if isinstance(user, AnonymousUser):
            raise BusinessRuleViolation(
                detail="Autenticação obrigatória para executar esta operação.",
                code="authentication_required",
            )
        return user

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
        planner = WeddingService._require_user(user)
        logger.info(
            f"Iniciando criação atómica de ecossistema para planner_id={planner.id}"
        )

        # 1. Extração de campos virtuais (não pertencem ao modelo Wedding)
        # o frontend envia "total_estimated" mas o modelo Wedding não o possui
        total_estimated = data.pop("total_estimated", None)

        # 2. Instanciação e Validação do Casamento
        wedding = Wedding(planner=planner, **data)
        wedding.save()

        # 3. Orquestração Financeira: Criar Orçamento Mestre
        # Passamos a instância 'wedding' diretamente para evitar queries extras
        budget = BudgetService.create(
            user=planner,
            data={"wedding": wedding, "total_estimated": total_estimated or 0},
        )

        # 4. Orquestração Financeira: Gerar Categorias Padrão (Blueprint)
        BudgetCategoryService.setup_defaults(
            user=planner, wedding=wedding, budget=budget
        )

        logger.info(
            f"Casamento criado com sucesso: uuid={wedding.uuid} com Orçamento e "
            f"Categorias."
        )
        return wedding

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: Wedding, data: dict[str, Any]
    ) -> Wedding:
        planner = WeddingService._require_user(user)
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} por planner_id={planner.id}"
        )

        # Defesa contra campos financeiros que não pertencem ao Wedding
        data.pop("total_estimated", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # Validação estrita (regras de negócio do Model)
        instance.save()

        logger.info(f"Casamento uuid={instance.uuid} atualizado.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: Wedding, data: dict[str, Any]
    ) -> Wedding:
        """Alias para atualização parcial para padronização."""
        return WeddingService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: Wedding) -> None:
        planner = WeddingService._require_user(user)
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
