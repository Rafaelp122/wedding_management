import logging
from typing import Any
from uuid import UUID

from django.db import transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.auth import require_user
from apps.core.exceptions import (
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.types import AuthContextUser
from apps.finances.models import Budget, BudgetCategory
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetCategoryService:
    """
    Camada de serviço para gestão de categorias de orçamento.
    Delega a validação matemática rigorosa de teto financeiro para o Model.
    """

    @staticmethod
    def list(
        user: AuthContextUser, wedding_id: UUID | None = None
    ) -> QuerySet[BudgetCategory]:
        """
        Lista categorias de orçamento de um planner.

        Nota de Arquitetura — ``wedding_id``:
        O parâmetro opcional ``wedding_id`` é uma conveniência de filtragem
        contextual, **não** um mecanismo de segurança. A multitenancy é
        garantida em todos os casos por ``BudgetCategory.objects.for_user``
        (herdado via ``WeddingOwnedMixin``), que isola os dados pelo ``planner``
        autenticado.

        Por que este filtro vive aqui e não na rota?
        ──────────────────────────────────────────────
        A regra de negócio é "cada casamento tem suas categorias isoladas".
        Filtrar por casamento é, portanto, lógica de domínio — não deve ser
        responsabilidade da camada de API (rotas) conhecer esse contexto.
        A rota apenas delega o parâmetro de query ao service, que decide como
        aplicá-lo sobre o queryset já protegido por tenancy.

        Args:
            user: Usuário autenticado (Planner).
            wedding_id: Quando informado, restringe as categorias a um
                casamento específico. O UUID do wedding é validado
                implicitamente pelo .for_user() — se o usuário não tem acesso
                ao casamento, o queryset retorna vazio.

        Returns:
            Queryset de ``BudgetCategory``, sempre escopado ao planner.
        """
        qs = BudgetCategory.objects.for_user(user).select_related("budget", "wedding")
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        return qs

    @staticmethod
    def get(user: AuthContextUser, uuid: UUID | str) -> BudgetCategory:
        try:
            return (
                BudgetCategory.objects.for_user(user)
                .select_related("budget", "wedding")
                .get(uuid=uuid)
            )
        except BudgetCategory.DoesNotExist as e:
            raise ObjectNotFoundError(
                detail="Categoria de orçamento não encontrada."
            ) from e

    @staticmethod
    @transaction.atomic
    def create(user: AuthContextUser, data: dict[str, Any]) -> BudgetCategory:
        planner = require_user(user)
        logger.info(
            f"Iniciando criação de Categoria de Orçamento para planner_id={planner.id}"
        )

        # 1. Resolução Segura do Orçamento Pai (Suporta Instância ou UUID)
        budget_input = data.pop("budget", None)

        if isinstance(budget_input, Budget):
            budget = budget_input
        else:
            try:
                # Segurança estrita: Garante posse do planner sobre o orçamento
                budget = Budget.objects.for_user(planner).get(uuid=budget_input)
            except Budget.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de orçamento inválido/negado: {budget_input}"
                )
                raise ObjectNotFoundError(
                    detail="Orçamento mestre não encontrado ou acesso negado.",
                    code="budget_not_found_or_denied",
                ) from e

        # 2. Injeção de Contexto e Instanciação
        category = BudgetCategory(wedding=budget.wedding, budget=budget, **data)

        # 3. Delegação de Validação ao Model
        # O método _validate_budget_ceiling que estava aqui DEVE ser movido
        # para dentro de BudgetCategory.clean(). Se o teto estourar, o Model
        # levantará ValidationError, e nosso Handler Global cuidará disso.
        category.save()

        logger.info(f"Categoria de Orçamento criada com sucesso: uuid={category.uuid}")
        return category

    @staticmethod
    @transaction.atomic
    def update(
        user: AuthContextUser, instance: BudgetCategory, data: dict[str, Any]
    ) -> BudgetCategory:
        planner = require_user(user)
        logger.info(
            f"Atualizando Categoria uuid={instance.uuid} por planner_id={planner.id}"
        )

        # Proteção contra sequestro/mudança de árvore financeira
        data.pop("budget", None)
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # A revalidação do teto financeiro com o novo 'allocated_budget'
        # ocorre automaticamente dentro do full_clean() do Model.
        instance.save()

        logger.info(f"Categoria uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def partial_update(
        user: AuthContextUser, instance: BudgetCategory, data: dict[str, Any]
    ) -> BudgetCategory:
        return BudgetCategoryService.update(user, instance, data)

    @staticmethod
    @transaction.atomic
    def delete(user: AuthContextUser, instance: BudgetCategory) -> None:
        planner = require_user(user)
        logger.info(
            f"Tentativa de deleção da Categoria uuid={instance.uuid} "
            f"por planner_id={planner.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Categoria uuid={instance.uuid} DESTRUÍDA por planner_id={planner.id}"
            )

        except ProtectedError as e:
            # Substitui a checagem manual .exists() pela trava real do banco de dados
            logger.error(
                f"Falha de integridade ao deletar Categoria uuid={instance.uuid}: "
                "Possui despesas ativas."
            )
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta categoria pois já existem "
                    "despesas vinculadas a ela. Remova as despesas primeiro."
                ),
                code="category_protected_error",
            ) from e

    @staticmethod
    def setup_defaults(user: AuthContextUser, wedding: Wedding, budget: Budget) -> None:
        """
        Cria as categorias iniciais obrigatórias para um novo casamento.

        Usa bulk_create para inserir todas as categorias em uma única query,
        evitando o overhead de full_clean() + validate_unique() + INSERT
        individual para cada uma das 6 categorias padrão.

        Isso é seguro porque os dados são hardcoded e controlados internamente,
        sem input do usuário.
        """
        DEFAULT_CATEGORIES = [
            "Espaço e Buffet",
            "Decoração e Flores",
            "Fotografia e Vídeo",
            "Música e Iluminação",
            "Assessoria",
            "Trajes e Beleza",
        ]

        logger.info(f"Gerando categorias padrão para o casamento {wedding.uuid}")

        categories = [
            BudgetCategory(
                wedding=wedding,
                budget=budget,
                name=name,
                allocated_budget=0,
            )
            for name in DEFAULT_CATEGORIES
        ]

        BudgetCategory.objects.bulk_create(categories)
