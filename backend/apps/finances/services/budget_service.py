import logging
from uuid import UUID

from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Budget
from apps.finances.schemas import BudgetIn, BudgetPatchIn
from apps.tenants.models import Company
from apps.weddings.models import Wedding


logger = logging.getLogger(__name__)


class BudgetService:
    """Camada de serviço para mutações e orquestração do orçamento mestre.

    Garante que cada casamento tenha exatamente um teto financeiro (OneToOne)
    e isola a lógica de negócio por tenant.

    Regras de Negócio:
        BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)
        BR-F06 (docs/architecture/business-rules/finances/tenant-budget-benchmark.md)
    """

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: BudgetIn) -> Budget:
        """Cria um novo orçamento mestre para um casamento.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Persiste atomicamente o orçamento mestre vinculado ao casamento.

        Raises:
            DomainIntegrityError: Se o casamento já possuir um orçamento.
            ObjectNotFoundError: Se o casamento informado não for encontrado ou não pertencer ao tenant.
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
                detail=(
                    f"Este casamento (uuid: '{wedding.uuid}') já possui um orçamento definido. "
                    "Atualize o existente em vez de criar outro."
                ),
                code="budget_already_exists",
            ) from e

        logger.info(f"Orçamento criado com sucesso: uuid={budget.uuid}")
        return budget

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Budget, payload: BudgetPatchIn) -> Budget:
        """Atualiza um orçamento existente.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Atualiza e persiste atomicamente as alterações no orçamento mestre.

        Raises:
            ObjectNotFoundError: Se o orçamento não for encontrado para o tenant.
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

        updated_fields: set[str] = set()
        data = payload.model_dump(exclude_unset=True)
        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        # O full_clean() garante a validação de regras como MinValueValidator
        if updated_fields:
            updated_fields.add("updated_at")
            instance.save(update_fields=list(updated_fields))

        logger.info(f"Orçamento uuid={instance.uuid} atualizado com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Budget) -> None:
        """Exclui um orçamento existente.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Remove fisicamente a instância do orçamento mestre do banco de dados.

        Raises:
            DomainIntegrityError: Se o orçamento possuir categorias ou despesas vinculadas.
            ObjectNotFoundError: Se o orçamento não for encontrado para o tenant.
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
            protected_count = len(e.protected_objects)
            raise DomainIntegrityError(
                detail=(
                    f"Não é possível apagar este orçamento principal (uuid: '{instance.uuid}') "
                    f"pois existem {protected_count} categorias e despesas vinculadas a ele."
                ),
                code="budget_protected_error",
            ) from e

    @staticmethod
    @transaction.atomic
    def get_or_create_for_wedding(company: Company, wedding_uuid: UUID | str) -> Budget:
        """Retorna o orçamento existente ou cria um novo para o casamento.

        Regra de Negócio:
            BR-F04 (docs/architecture/business-rules/finances/budget-category-distribution.md)

        Efeitos Colaterais:
            - Cria o orçamento mestre e gera categorias canônicas padrão caso ainda não exista.

        Raises:
            ObjectNotFoundError: Se o casamento não for encontrado para o tenant.
        """
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
