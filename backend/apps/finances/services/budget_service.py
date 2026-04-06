import logging
from typing import Any
from uuid import UUID

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.finances.models import Budget
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """
    Camada de serviço para gestão do orçamento mestre.
    Garante que cada casamento tenha exatamente UM teto financeiro (OneToOne).
    """

    @staticmethod
    def list(user: AuthContextUser) -> QuerySet[Budget]:
        return Budget.objects.for_user(user).select_related("wedding")

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> Budget:
        try:
            return (
                Budget.objects.for_user(user).select_related("wedding").get(uuid=uuid)
            )
        except Budget.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Orçamento não encontrado.") from e

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> Budget:
        planner = require_user(user)
        logger.info(
            f"Iniciando criação de Orçamento Mestre para planner_id={planner.id}"
        )

        # 1. Resolução Segura do Casamento (Suporta Instância ou UUID)
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.for_user(planner).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de criar orçamento para casamento "
                    f"inválido/negado: {wedding_input}"
                )
                raise ObjectNotFoundError(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória
        budget = Budget(wedding=wedding, **data)

        # 3. Validação e Persistência
        try:
            budget.save()
        except IntegrityError as e:
            # O banco apita se já existir um Budget para este Wedding (OneToOneField)
            logger.error(
                f"Conflito de integridade: Casamento uuid={wedding.uuid} já possui "
                f"orçamento."
            )
            raise DomainIntegrityError(
                detail="Este casamento já possui um orçamento definido. Atualize o "
                "existente em vez de criar outro.",
                code="budget_already_exists",
            ) from e

        logger.info(f"Orçamento criado com sucesso: uuid={budget.uuid}")
        return budget

    @staticmethod
    @transaction.atomic
    def update(user: AuthContextUser, instance: Budget, data: dict[str, Any]) -> Budget:
        planner = require_user(user)
        logger.info(
            f"Atualizando Orçamento uuid={instance.uuid} por planner_id={planner.id}"
        )

        # Proteção contra sequestro de propriedade e realocação
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() garante a validação de regras como MinValueValidator
        instance.save()

        logger.info(f"Orçamento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: Budget, data: dict[str, Any]
    ) -> Budget:
        return BudgetService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: Budget) -> None:
        planner = require_user(user)
        logger.info(
            f"Tentativa de deleção do Orçamento uuid={instance.uuid} por "
            f"planner_id={planner.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Orçamento uuid={instance.uuid} DESTRUÍDO por planner_id={planner.id}"
            )

        except ProtectedError as e:
            logger.error(
                f"Falha de integridade ao deletar Orçamento uuid={instance.uuid}: "
                "Protegido por relações filhas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este orçamento principal pois existem "
                "categorias e despesas vinculadas a ele.",
                code="budget_protected_error",
            ) from e

    @staticmethod
    @transaction.atomic
    def get_or_create_for_wedding(
        user: AuthContextUser, wedding_uuid: UUID | str
    ) -> Budget:
        """
        Retorna o Budget existente ou cria um novo para o Wedding especificado.

        Este método implementa o padrão Lazy Loading para Budget:
        - O Budget só é criado quando realmente necessário (primeira visualização)
        - Evita dados fake (total_estimated=0) no momento da criação do Wedding
        - Cria automaticamente as categorias padrão junto com o Budget

        Args:
            user: Usuário autenticado (Planner)
            wedding_uuid: UUID do casamento

        Returns:
            Budget: Instância existente ou recém-criada

        Raises:
            BusinessRuleViolation: Se o casamento não existir ou acesso negado
        """
        from apps.finances.services.budget_category_service import BudgetCategoryService
        from apps.weddings.models import Wedding

        planner = require_user(user)

        # 1. Validação de Acesso: Garante que o Wedding pertence ao usuário
        try:
            wedding = Wedding.objects.for_user(planner).get(uuid=wedding_uuid)
        except Wedding.DoesNotExist as e:
            logger.warning(
                f"Tentativa de criar orçamento para casamento inválido/negado: "
                f"{wedding_uuid} por planner_id={planner.id}"
            )
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            ) from e

        # 2. Get or Create: Usa get_or_create do Django (thread-safe)
        budget, created = Budget.objects.get_or_create(
            wedding=wedding,
            defaults={"total_estimated": 0},
        )

        # 3. Setup Inicial: Cria categorias padrão se Budget foi recém-criado
        if created:
            logger.info(
                f"Budget criado sob demanda para wedding={wedding.uuid}, "
                f"criando categorias padrão..."
            )
            BudgetCategoryService.setup_defaults(
                user=user, wedding=wedding, budget=budget
            )
            logger.info(
                f"Budget uuid={budget.uuid} + categorias criados para "
                f"wedding={wedding.uuid}"
            )
        else:
            logger.debug(f"Budget existente retornado: uuid={budget.uuid}")

        return budget
