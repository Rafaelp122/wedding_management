from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import datetime, time, timedelta
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count, OuterRef, ProtectedError, Q, QuerySet, Subquery
from django.db.models.functions import Coalesce

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Budget
from apps.scheduler.schemas import EventIn
from apps.tenants.models import Company

from ..models import Wedding
from ..schemas import (
    WeddingDashboardCategoryOut,
    WeddingDashboardInstallmentOut,
    WeddingDashboardOut,
    WeddingDashboardTaskOut,
    WeddingIn,
    WeddingOut,
    WeddingOverviewOut,
    WeddingPatchIn,
)


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.

    Nota: Budget e suas categorias são criados sob demanda (lazy loading)
    através do BudgetService.get_or_create_for_wedding().
    """

    @staticmethod
    def list(company: Company, search: str = "", status: str = "") -> QuerySet[Wedding]:
        """
        Lista os casamentos associados à empresa com filtros e anotações.

        Permite busca textual por nomes dos noivos/local e filtragem por status.
        Anota de forma otimizada o orçamento estimado total, contagem de parcelas
        em atraso e de tarefas incompletas usando Subqueries.

        Args:
            company: O tenant atual para isolamento de dados.
            search: Termo de busca para filtrar por noivos ou local.
            status: Filtro por status do casamento (ex: IN_PROGRESS).

        Returns:
            QuerySet contendo os casamentos correspondentes e anotados.

        Raises:
            BusinessRuleViolation: Se o status de filtro fornecido for inválido.
        """
        qs = Wedding.objects.for_tenant(company).select_related("company")
        if search:
            qs = qs.filter(
                Q(groom_name__icontains=search)
                | Q(bride_name__icontains=search)
                | Q(location__icontains=search)
            )
        if status:
            if status not in Wedding.StatusChoices.values:
                raise BusinessRuleViolation(
                    detail=f"Status inválido: '{status}'.",
                    code="wedding_invalid_status_filter",
                )
            qs = qs.filter(status=status)

        from apps.finances.models import Installment
        from apps.scheduler.models import Task

        # Otimização: Uso de Subqueries para contagem ao invés de Count(distinct=True)
        # para evitar a explosão do produto cartesiano (JOIN explosion) quando
        # múltiplos conjuntos relacionados são contados na mesma query.
        qs = qs.annotate(
            total_budget=Subquery(
                Budget.objects.filter(
                    wedding=OuterRef("pk"), company=OuterRef("company")
                ).values("total_estimated")[:1]
            ),
            overdue_installments=Coalesce(
                Subquery(
                    Installment.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        status="OVERDUE",
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
            incomplete_tasks=Coalesce(
                Subquery(
                    Task.objects.filter(
                        wedding=OuterRef("pk"),
                        company=OuterRef("company"),
                        is_completed=False,
                    )
                    .values("wedding")
                    .annotate(cnt=Count("id"))
                    .values("cnt")[:1]
                ),
                0,
            ),
        )  # type: ignore[assignment]

        return qs

    @staticmethod
    def list_lookup(company: Company) -> QuerySet[Wedding]:
        """
        Retorna uma lista simplificada de casamentos associados à empresa.

        Esta lista é otimizada para ser utilizada em componentes de busca rápida
        ou caixas de seleção (comboboxes), selecionando apenas os campos necessários.

        Args:
            company: O tenant atual para isolamento de dados.

        Returns:
            QuerySet contendo os casamentos com campos restritos a uuid,
            bride_name e groom_name, ordenados pelo nome da noiva.
        """
        return (
            Wedding.objects.for_tenant(company)
            .only("uuid", "bride_name", "groom_name")
            .order_by("bride_name")
        )

    @staticmethod
    def count_by_month(company: Company, year: int) -> Sequence[dict]:
        """
        Agrupa e conta os casamentos por mês para um determinado ano.

        Args:
            company: O tenant atual para isolamento de dados.
            year: O ano correspondente para filtragem dos casamentos.

        Returns:
            Sequência de dicionários com chaves 'month' e 'count',
            ordenada cronologicamente pelo mês.
        """
        qs = (
            Wedding.objects.for_tenant(company)
            .filter(date__year=year)
            .values("date__month")
            .annotate(count=Count("id"))
            .order_by("date__month")
        )
        return [{"month": item["date__month"], "count": item["count"]} for item in qs]

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Wedding:
        """
        Recupera um casamento pelo UUID validando o tenant.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: O UUID ou representação em string do casamento.

        Returns:
            A instância do casamento solicitada.

        Raises:
            HttpError: Se o casamento não pertencer à empresa ou não existir.
        """
        return get_object_or_404_for_tenant(
            Wedding,
            company,
            uuid,
            select_related=["company"],
            code="wedding_not_found_or_denied",
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: WeddingIn) -> Wedding:
        """
        Cria um novo casamento e opcionalmente aplica um template de cronograma.

        Realiza a persistência do casamento após validar os dados de entrada
        com o método full_clean(). Se especificado no payload, agenda
        automaticamente os eventos de template configurados.

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para criação do casamento.

        Returns:
            A instância de Wedding criada e salva no banco de dados.

        Raises:
            BusinessRuleViolation: Se houver erro de validação nos dados fornecidos.
        """
        logger.info(f"Criando casamento para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        model_data = {k: v for k, v in data.items() if k in valid_fields}

        # Instanciação e Validação do Casamento
        wedding = Wedding(company=company, **model_data)
        try:
            wedding.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao criar casamento para company_id={company.id}: "
                f"{e}"
            )
            detail = "; ".join(e.messages) if e.messages else str(e)
            raise BusinessRuleViolation(
                detail=detail,
                code="wedding_validation_error",
            ) from e

        # ── Template de Cronograma ────────────────────────────────────────
        template_name = data.get("template")
        if template_name is not None:
            logger.info(
                f"Aplicando template '{template_name}' ao casamento uuid={wedding.uuid}"
            )
            _apply_template_events(company, wedding, template_name)

        logger.info(f"Casamento criado com sucesso: uuid={wedding.uuid}")
        return wedding

    @staticmethod
    @transaction.atomic
    def update(company: Company, instance: Wedding, payload: WeddingPatchIn) -> Wedding:
        """
        Atualiza dados de um casamento existente com base no payload fornecido.

        Garante isolamento de tenant antes de atualizar e executa validações
        com full_clean() antes de persistir as modificações.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância atual de Wedding a ser atualizada.
            payload: Campos modificados a serem aplicados no casamento.

        Returns:
            A instância do casamento atualizada e salva.

        Raises:
            BusinessRuleViolation: Se a atualização violar regras de negócio ou de
                validação do modelo.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} pela company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        valid_fields = {f.name for f in Wedding._meta.concrete_fields}
        for field, value in data.items():
            if field in valid_fields:
                setattr(instance, field, value)

        # Validação estrita
        try:
            instance.save()
        except DjangoValidationError as e:
            logger.warning(
                f"Falha de validação ao atualizar casamento uuid={instance.uuid} "
                f"pela company_id={company.id}: {e}"
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
    def delete(company: Company, instance: Wedding) -> None:
        """
        Deleta um casamento existente validando a propriedade de tenant.

        Previne a deleção caso existam contratos ou despesas protegidos
        por chaves estrangeiras vinculadas.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: Instância de Wedding a ser deletada.

        Raises:
            DomainIntegrityError: Se houver violação de integridade ou se
                o casamento possuir relacionamentos protegidos.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
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
            logger.exception(
                f"Falha de integridade: Casamento uuid={instance.uuid} protegido por "
                f"contratos/despesas."
            )
            raise DomainIntegrityError(
                detail="Não é possível apagar este casamento pois existem contratos ou "
                "despesas vinculadas a ele.",
                code="wedding_protected_error",
            ) from e

    @staticmethod
    def overview(company: Company, uuid: UUID | str) -> WeddingOverviewOut:
        """
        Retorna visão geral do casamento com métricas agregadas.

        Busca dados de orçamento, tarefas, contratos e parcelas do casamento
        para compor a visão geral usada na tela de detalhes.

        Args:
            company: O tenant atual para isolamento de dados.
            uuid: UUID do casamento a ser consultado.

        Returns:
            WeddingOverviewOut com dados do casamento e métricas.

        Raises:
            ObjectNotFoundError: Se o casamento não existir ou não pertencer ao tenant.
        """
        from datetime import date as date_type

        wedding = get_object_or_404_for_tenant(
            Wedding,
            company,
            uuid,
            select_related=["company"],
            code="wedding_not_found_or_denied",
        )

        today = date_type.today()
        days_until = max(0, (wedding.date - today).days) if wedding.date else 0

        from apps.finances.models import Budget, BudgetCategory, Installment
        from apps.logistics.models import Contract
        from apps.scheduler.models import Task

        budget = (
            Budget.objects.for_tenant(company)
            .filter(wedding=wedding)
            .with_total_spent()
            .first()
        )
        total_estimated = budget.total_estimated if budget else 0.0
        total_spent = getattr(budget, "_total_overall_spent", 0) if budget else 0.0
        budget_pct = (
            round((float(total_spent) / float(total_estimated)) * 100, 1)
            if total_estimated > 0
            else 0.0
        )

        categories_list = (
            BudgetCategory.objects.for_tenant(company)
            .filter(budget=budget)
            .with_total_spent()
            if budget
            else []
        )
        categories_summary = [
            WeddingDashboardCategoryOut(
                name=cat.name,
                allocated=str(cat.allocated_budget),
                spent=str(cat._total_spent),
                percentage=(
                    round(
                        float(cat._total_spent) / float(cat.allocated_budget) * 100,
                        1,
                    )
                    if cat.allocated_budget and float(cat.allocated_budget) > 0
                    else 0.0
                ),
            )
            for cat in categories_list
        ]

        tasks = Task.objects.for_tenant(company).filter(wedding=wedding)
        tasks_total = tasks.count()
        tasks_completed = tasks.filter(is_completed=True).count()
        urgent_tasks_qs = tasks.filter(
            is_completed=False, due_date__lte=today
        ).order_by("due_date")[:5]
        urgent_tasks_out = [
            WeddingDashboardTaskOut(uuid=t.uuid, title=t.title, due_date=t.due_date)
            for t in urgent_tasks_qs
        ]
        incomplete_tasks = tasks.filter(is_completed=False).count()

        contracts = Contract.objects.for_tenant(company).filter(wedding=wedding)
        contracts_total = contracts.count()
        contracts_signed = contracts.filter(status="SIGNED").count()

        installments = (
            Installment.objects.for_tenant(company)
            .filter(wedding=wedding, status__in=["PENDING", "OVERDUE"])
            .order_by("due_date")[:10]
        )
        upcoming_out = [
            WeddingDashboardInstallmentOut(
                uuid=i.uuid,
                installment_number=i.installment_number,
                amount=str(i.amount),
                due_date=i.due_date,
                status=i.status,
            )
            for i in installments
        ]
        overdue_count = (
            Installment.objects.for_tenant(company)
            .filter(wedding=wedding, status="OVERDUE")
            .count()
        )

        wedding_out = WeddingOut(
            uuid=wedding.uuid,
            groom_name=wedding.groom_name,
            bride_name=wedding.bride_name,
            date=wedding.date,
            location=wedding.location,
            expected_guests=wedding.expected_guests,
            status=(
                wedding.status.value
                if hasattr(wedding.status, "value")
                else wedding.status
            ),
            template=wedding.template,
            created_at=wedding.created_at,
            updated_at=wedding.updated_at,
            total_budget=total_estimated,
            overdue_installments=overdue_count,
            incomplete_tasks=incomplete_tasks,
        )

        return WeddingOverviewOut(
            wedding=wedding_out,
            overview=WeddingDashboardOut(
                days_until_wedding=days_until,
                budget_percentage_used=budget_pct,
                tasks_completed=tasks_completed,
                tasks_total=tasks_total,
                contracts_signed=contracts_signed,
                contracts_total=contracts_total,
                upcoming_installments=upcoming_out,
                urgent_tasks=urgent_tasks_out,
                categories_summary=categories_summary,
            ),
        )


@transaction.atomic
def _apply_template_events(
    company: Company, wedding: Wedding, template_name: str
) -> None:
    """
    Aplica um template de cronograma criando eventos para o casamento.

    Calcula a data de início de cada evento usando a quantidade de dias
    especificada como offset relativo à data do casamento.

    Args:
        company: O tenant atual para isolamento de dados.
        wedding: O casamento a receber os eventos do template.
        template_name: O identificador/nome do template a ser aplicado.
    """
    from django.utils import timezone

    from apps.scheduler.services import EventService
    from apps.scheduler.services.templates import get_template_events

    template_events = get_template_events(template_name)

    for event_data in template_events:
        offset_days = int(event_data["offset_days"])
        naive_start = datetime.combine(
            wedding.date - timedelta(days=offset_days),
            time(hour=9, minute=0),
        )
        event_start = timezone.make_aware(naive_start)

        EventService.create(
            company,
            EventIn(
                wedding=wedding.uuid,
                title=event_data["title"],
                event_type=event_data["event_type"],
                start_time=event_start,
                location="",
                description="",
            ),
        )
