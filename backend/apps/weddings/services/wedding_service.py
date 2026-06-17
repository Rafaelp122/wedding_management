import logging
from datetime import datetime, time, timedelta
from typing import Any
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import Count, OuterRef, ProtectedError, Q, QuerySet, Subquery

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.finances.models import Budget
from apps.tenants.models import Company

from ..models import Wedding


logger = logging.getLogger(__name__)


class WeddingService:
    """
    Camada de serviço para gerenciar a lógica de negócio de casamentos.

    Nota: Budget e suas categorias são criados sob demanda (lazy loading)
    através do BudgetService.get_or_create_for_wedding().
    """

    @staticmethod
    def list(company: Company, search: str = "", status: str = "") -> QuerySet[Wedding]:
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

        qs = qs.annotate(
            total_budget=Subquery(
                Budget.objects.filter(
                    wedding=OuterRef("pk"), company=OuterRef("company")
                ).values("total_estimated")[:1]
            ),
            overdue_installments=Count(
                "installment_records",
                filter=Q(installment_records__status="OVERDUE"),
                distinct=True,
            ),
            incomplete_tasks=Count(
                "task_records",
                filter=Q(task_records__is_completed=False),
                distinct=True,
            ),
        )  # type: ignore[assignment]

        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Wedding:
        wedding = Wedding.objects.for_tenant(company).filter(uuid=uuid).first()
        if wedding is None:
            raise ObjectNotFoundError(
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )
        return wedding

    @staticmethod
    @transaction.atomic
    def create(company: Company, data: dict[str, Any]) -> Wedding:
        logger.info(f"Criando casamento para company_id={company.id}")

        # Filtra apenas os campos que pertencem ao modelo Wedding
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
    def update(company: Company, instance: Wedding, data: dict[str, Any]) -> Wedding:
        logger.info(
            f"Atualizando casamento uuid={instance.uuid} pela company_id={company.id}"
        )

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
        Deleta um casamento.
        """
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
    Aplica um template de cronograma ao casamento, criando eventos
    com base no offset em dias antes da data do casamento.

    Importação lazy do EventService para evitar circular imports.
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
            {
                "wedding": wedding,
                "title": event_data["title"],
                "event_type": event_data["event_type"],
                "start_time": event_start,
            },
        )
