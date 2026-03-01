import logging

from django.db import transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import Budget, BudgetCategory


logger = logging.getLogger(__name__)


class BudgetCategoryService:
    """
    Camada de serviço para gestão de categorias de orçamento.
    Delega a validação matemática rigorosa de teto financeiro para o Model.
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> BudgetCategory:
        logger.info(
            f"Iniciando criação de Categoria de Orçamento para planner_id={user.id}"
        )

        # 1. Resolução Segura do Orçamento Pai (Suporta Instância ou UUID)
        budget_input = data.pop("budget", None)

        if isinstance(budget_input, Budget):
            budget = budget_input
        else:
            try:
                # Segurança estrita: Garante posse do planner sobre o orçamento
                budget = Budget.objects.all().for_user(user).get(uuid=budget_input)
            except Budget.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de orçamento inválido/negado: {budget_input}"
                )
                raise BusinessRuleViolation(
                    detail="Orçamento mestre não encontrado ou acesso negado.",
                    code="budget_not_found_or_denied",
                ) from e

        # 2. Injeção de Contexto e Instanciação
        category = BudgetCategory(
            wedding=budget.wedding, budget=budget, **data
        )

        # 3. Delegação de Validação ao Model
        # O método _validate_budget_ceiling que estava aqui DEVE ser movido
        # para dentro de BudgetCategory.clean(). Se o teto estourar, o Model
        # levantará ValidationError, e nosso Handler Global cuidará disso.
        category.save()

        logger.info(f"Categoria de Orçamento criada com sucesso: uuid={category.uuid}")
        return category

    @staticmethod
    @transaction.atomic
    def update(user, instance: BudgetCategory, data: dict) -> BudgetCategory:
        logger.info(
            f"Atualizando Categoria uuid={instance.uuid} por planner_id={user.id}"
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
    def delete(user, instance: BudgetCategory) -> None:
        logger.info(
            f"Tentativa de deleção da Categoria uuid={instance.uuid} "
            f"por planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Categoria uuid={instance.uuid} DESTRUÍDA por planner_id={user.id}"
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
    def setup_defaults(user, wedding, budget):
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
