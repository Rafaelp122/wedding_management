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
from ..schemas import WeddingIn, WeddingPatchIn


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
