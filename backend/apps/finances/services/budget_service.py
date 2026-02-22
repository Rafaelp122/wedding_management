import logging

from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.finances.models import Budget
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """
    Camada de serviço para gestão do orçamento mestre.
    Garante que cada casamento tenha exatamente UM teto financeiro (OneToOne).
    """

    @staticmethod
    @transaction.atomic
    def create(user, data: dict) -> Budget:
        logger.info(f"Iniciando criação de Orçamento Mestre para planner_id={user.id}")

        # 1. Resolução Segura do Casamento (Suporta Instância ou UUID)
        wedding_input = data.pop("wedding", None)

        if isinstance(wedding_input, Wedding):
            wedding = wedding_input
        else:
            try:
                wedding = Wedding.objects.all().for_user(user).get(uuid=wedding_input)
            except Wedding.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de criar orçamento para casamento "
                    f"inválido/negado: {wedding_input}"
                )
                raise BusinessRuleViolation(
                    detail="Casamento não encontrado ou acesso negado.",
                    code="wedding_not_found_or_denied",
                ) from e

        # 2. Instanciação em Memória
        budget = Budget(wedding=wedding, **data)

        # 3. Validação e Persistência
        try:
            budget.full_clean()
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
    def update(instance: Budget, user, data: dict) -> Budget:
        logger.info(
            f"Atualizando Orçamento uuid={instance.uuid} por planner_id={user.id}"
        )

        # Proteção contra sequestro de propriedade e realocação
        data.pop("wedding", None)
        data.pop("planner", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() garante a validação de regras como MinValueValidator
        instance.full_clean()
        instance.save()

        logger.info(f"Orçamento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(user, instance: Budget) -> None:
        logger.info(
            f"Tentativa de deleção do Orçamento uuid={instance.uuid} por "
            "planner_id={user.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Orçamento uuid={instance.uuid} DESTRUÍDO por planner_id={user.id}"
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
