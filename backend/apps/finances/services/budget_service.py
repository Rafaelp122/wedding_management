import logging
from typing import cast
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError, QuerySet

from apps.core.exceptions import DomainIntegrityError
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.managers import BudgetQuerySet
from apps.finances.models import Budget
from apps.finances.schemas import BudgetIn, BudgetPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """Camada de serviço para gestão do orçamento mestre.

    Garante que cada casamento tenha exatamente um teto financeiro (OneToOne)
    e isola a lógica de negócio por tenant.
    """

    @staticmethod
    def list(company: Company) -> QuerySet[Budget]:
        """Lista os orçamentos de uma empresa.

        Args:
            company: O tenant atual para isolamento de dados.

        Returns:
            QuerySet[Budget]: QuerySet com os orçamentos contendo o gasto total.
        """
        return (
            cast(BudgetQuerySet, Budget.objects.for_tenant(company))
            .with_total_spent()
            .select_related("wedding")
        )

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Budget:
        """Obtém um orçamento específico pelo seu UUID.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: O UUID do orçamento desejado.

        Returns:
            Budget: A instância do orçamento encontrada.

        Raises:
            ObjectNotFoundError: Se o orçamento não for encontrado.
        """
        try:
            return (
                cast(BudgetQuerySet, Budget.objects.for_tenant(company))
                .with_total_spent()
                .select_related("wedding")
                .get(uuid=uuid)
            )
        except (Budget.DoesNotExist, ValueError, ValidationError) as e:
            from apps.core.exceptions import ObjectNotFoundError

            raise ObjectNotFoundError(
                detail="Orçamento não encontrado ou acesso negado."
            ) from e

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: BudgetIn) -> Budget:
        """Cria um novo orçamento mestre para um casamento.

        Garante que casamentos não tenham orçamentos duplicados (restrição
        OneToOne).

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do orçamento.

        Returns:
            Budget: A instância do orçamento criada.

        Raises:
            DomainIntegrityError: Se o casamento já possuir um orçamento.
        """
        logger.info(
            f"Iniciando criação de Orçamento Mestre para company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        wedding_input = data.pop("wedding", None)

        wedding = resolve_tenant_resource(
            Wedding,
            company,
            wedding_input,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )

        # 2. Instanciação em Memória
        budget = Budget(company=company, wedding=wedding, **data)

        # 3. Validação e Persistência
        try:
            budget.save()
        except (IntegrityError, ValidationError) as e:
            if isinstance(e, ValidationError):
                message_dict = getattr(e, "message_dict", {})
                other_fields = [k for k in message_dict if k != "wedding"]
                if other_fields:
                    raise e

            logger.exception(
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
    def update(company: Company, instance: Budget, payload: BudgetPatchIn) -> Budget:
        """Atualiza um orçamento existente.

        Garante o isolamento do tenant e valida as regras de negócios como
        o validador de valor mínimo.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do orçamento a ser atualizada.
            payload: Dados parciais para atualização do orçamento.

        Returns:
            Budget: A instância do orçamento atualizada.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Orçamento uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)
        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        # O full_clean() garante a validação de regras como MinValueValidator
        instance.save()

        logger.info(f"Orçamento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Budget) -> None:
        """Exclui um orçamento existente.

        Verifica a propriedade do tenant e se o orçamento está protegido por
        categorias ou despesas filhas antes de prosseguir com a exclusão.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância do orçamento a ser excluída.

        Raises:
            DomainIntegrityError: Se o orçamento possuir categorias ou despesas.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção do Orçamento uuid={instance.uuid} por "
            f"company_id={company.id}"
        )

        try:
            instance.delete()
            logger.warning(
                f"Orçamento uuid={instance.uuid} DESTRUÍDO por company_id={company.id}"
            )

        except ProtectedError as e:
            logger.exception(
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
    def get_or_create_for_wedding(company: Company, wedding_uuid: UUID | str) -> Budget:
        """Retorna o orçamento existente ou cria um novo para o casamento.

        Se for criado, também gera automaticamente as categorias padrão
        do orçamento sob lock (select_for_update) para evitar condições de corrida.

        Args:
            company: O tenant atual para isolamento de dados.
            wedding_uuid: O UUID do casamento associado.

        Returns:
            Budget: A instância do orçamento (existente ou recém-criado).
        """
        from apps.weddings.models import Wedding

        wedding = get_object_or_404_for_tenant(
            Wedding,
            company,
            wedding_uuid,
            code="wedding_not_found_or_denied",
        )

        budget, created = Budget.objects.get_or_create(
            company=company,
            wedding=wedding,
            defaults={"total_estimated": 0},
        )

        if created:
            # TRAVA DE SEGURANÇA (TOCTOU): serializa criação de categorias padrão
            budget = (
                Budget.objects.for_tenant(company).select_for_update().get(pk=budget.pk)
            )

            from apps.finances.services.budget_category_service import (
                BudgetCategoryService,
            )

            logger.info(
                f"Budget criado sob demanda para wedding={wedding.uuid}. "
                f"Criando categorias padrão."
            )
            BudgetCategoryService.setup_defaults(
                company=company,
                wedding=wedding,
                budget=budget,
            )
            logger.info(
                f"Budget uuid={budget.uuid} + categorias criados para "
                f"wedding={wedding.uuid}"
            )
        else:
            logger.debug(f"Budget existente retornado: uuid={budget.uuid}")

        return budget
