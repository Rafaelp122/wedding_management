from __future__ import annotations

import logging
from datetime import date
from uuid import UUID

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.db.models import QuerySet

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
    ObjectNotFoundError,
)
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Expense, Installment
from apps.finances.schemas import InstallmentAdjustIn, InstallmentIn, InstallmentPatchIn
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class InstallmentService:
    """
    Camada de serviço para orquestração de Parcelas.
    Garante o isolamento multitenant e a integridade da Tolerância Zero (ADR-010)
    nas despesas pai.
    """

    @staticmethod
    def list(
        company: Company,
        wedding_id: UUID | str | None = None,
        expense_id: UUID | str | None = None,
    ) -> QuerySet[Installment]:
        qs = Installment.objects.for_tenant(company).select_related(
            "expense", "wedding"
        )
        if wedding_id:
            qs = qs.filter(wedding__uuid=wedding_id)
        if expense_id:
            qs = qs.filter(expense__uuid=expense_id)
        return qs

    @staticmethod
    def get(company: Company, uuid: UUID | str) -> Installment:
        try:
            return (
                Installment.objects.for_tenant(company)
                .select_related("expense", "wedding")
                .get(uuid=uuid)
            )
        except Installment.DoesNotExist as e:
            raise ObjectNotFoundError(detail="Parcela não encontrada.") from e

    @staticmethod
    @transaction.atomic
    def auto_generate_installments(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date,
    ) -> list[Installment]:  # type: ignore[valid-type]
        """
        Gera automaticamente as parcelas de uma despesa com ajuste na última
        parcela (Tolerância Zero).

        Para cada parcela gerada, também cria um evento PAYMENT no scheduler
        (BR-S01) para que o casal visualize os compromissos de pagamento no
        calendário.
        """
        from datetime import timedelta

        # Bloqueio de reentrada/duplicação (Copilot Review Fix)
        if expense.installments.exists():
            raise BusinessRuleViolation(
                detail=(
                    "Esta despesa já possui parcelas geradas. Remova-as "
                    "antes de gerar novas."
                ),
                code="installments_already_exist",
            )

        if num_installments <= 0:
            raise BusinessRuleViolation(
                detail="O número de parcelas deve ser maior que zero.",
                code="invalid_installment_number",
            )

        if not expense.actual_amount or expense.actual_amount <= 0:
            raise BusinessRuleViolation(
                detail="A despesa precisa ter um valor maior que zero para "
                "parcelamento.",
                code="invalid_expense_amount",
            )

        base_amount = round(expense.actual_amount / num_installments, 2)
        installments: list[Installment] = []

        current_due_date = first_due_date

        for i in range(1, num_installments):
            installments.append(
                Installment(
                    company=company,
                    wedding=expense.wedding,
                    expense=expense,
                    installment_number=i,
                    amount=base_amount,
                    due_date=current_due_date,
                    status=Installment.StatusChoices.PENDING,
                )
            )
            current_due_date += timedelta(days=30)

        last_amount = expense.actual_amount - (base_amount * (num_installments - 1))
        installments.append(
            Installment(
                company=company,
                wedding=expense.wedding,
                expense=expense,
                installment_number=num_installments,
                amount=last_amount,
                due_date=current_due_date,
                status=Installment.StatusChoices.PENDING,
            )
        )

        # Usar .save() em vez de bulk_create para garantir que full_clean()
        # e hooks do BaseModel/Tolerância Zero sejam executados (ADR-011)
        for inst in installments:
            inst.save()

        # ── Auto-geração de Eventos PAYMENT (BR-S01) ──────────────────────
        _create_payment_events(company, expense, installments)

        return installments

    @staticmethod
    @transaction.atomic
    def redistribute(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date,
    ) -> list[Installment]:  # type: ignore[valid-type]
        if expense.installments.filter(status="PAID").exists():
            raise BusinessRuleViolation(
                detail=(
                    "Não é possível alterar o número de parcelas — existem "
                    "parcelas já marcadas como pagas. Crie uma nova despesa."
                ),
                code="redistribute_blocked_by_paid",
            )

        _delete_payment_events_for_expense(company, expense)
        expense.installments.all().delete()
        return InstallmentService.auto_generate_installments(
            company=company,
            expense=expense,
            num_installments=num_installments,
            first_due_date=first_due_date,
        )

    @staticmethod
    @transaction.atomic
    def create(company: Company, payload: InstallmentIn) -> Installment:
        logger.info(f"Iniciando criação de Parcela para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        expense_input = data.pop("expense", None)
        if isinstance(expense_input, Expense):
            expense = expense_input
        else:
            try:
                expense = Expense.objects.for_tenant(company).get(uuid=expense_input)
            except Expense.DoesNotExist as e:
                logger.warning(
                    f"Tentativa de uso de despesa inválida/negada: {expense_input}"
                )
                raise ObjectNotFoundError(
                    detail="Despesa não encontrada ou acesso negado.",
                    code="expense_not_found_or_denied",
                ) from e

        # 2. Injeção de Contexto e Instanciação
        installment = Installment(
            company=company, wedding=expense.wedding, expense=expense, **data
        )

        # 3. Validação Estrita da Parcela
        installment.save()

        # 4. Checagem de Ricochete (Tolerância Zero)
        try:
            expense.full_clean()
        except DjangoValidationError as e:
            logger.exception(
                f"Criação de parcela violou Tolerância Zero da despesa "
                f"uuid={expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail=(
                    "A criação desta parcela gera uma inconsistência matemática "
                    "na despesa total (ADR-010). O valor das parcelas deve bater "
                    "exatamente com o total."
                ),
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela criada com sucesso: uuid={installment.uuid}")
        return installment

    @staticmethod
    @transaction.atomic
    def update(
        company: Company,
        instance: Installment,
        payload: InstallmentPatchIn,
    ) -> Installment:
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Parcela uuid={instance.uuid} por company_id={company.id}"
        )

        data = payload.model_dump(exclude_unset=True)

        data.pop("expense", None)
        data.pop("wedding", None)
        data.pop("company", None)

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        # Revalidação da Despesa Pai (Tolerância Zero)
        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            logger.exception(
                f"Atualização de parcela quebrou Tolerância Zero na despesa "
                f"uuid={instance.expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail="A atualização desta parcela viola as regras matemáticas da "
                "despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela uuid={instance.uuid} atualizada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def mark_as_paid(company: Company, instance: Installment) -> Installment:
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        if instance.status == Installment.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail="Esta parcela já foi marcada como paga.",
                code="installment_already_paid",
            )

        instance.status = Installment.StatusChoices.PAID
        instance.paid_date = date.today()
        instance.save()

        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            logger.exception(
                f"Marcação de parcela quebrou Tolerância Zero na despesa "
                f"uuid={instance.expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail="Marcar esta parcela como paga viola as regras matemáticas "
                "da despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela uuid={instance.uuid} marcada como paga.")
        return instance

    @staticmethod
    @transaction.atomic
    def unmark_as_paid(company: Company, instance: Installment) -> Installment:
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        if instance.status != Installment.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail="Apenas parcelas marcadas como pagas podem ser desmarcadas.",
                code="installment_not_paid",
            )

        instance.paid_date = None
        if instance.due_date < date.today():
            instance.status = Installment.StatusChoices.OVERDUE
        else:
            instance.status = Installment.StatusChoices.PENDING
        instance.save()

        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            logger.exception(
                f"Desmarcação de parcela quebrou Tolerância Zero na despesa "
                f"uuid={instance.expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail="Desmarcar esta parcela viola as regras matemáticas "
                "da despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela uuid={instance.uuid} desmarcada como paga.")
        return instance

    @staticmethod
    @transaction.atomic
    def adjust(
        company: Company, instance: Installment, payload: InstallmentAdjustIn
    ) -> Installment:
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        if instance.status == Installment.StatusChoices.PAID:
            raise BusinessRuleViolation(
                detail="Não é possível ajustar uma parcela já marcada como paga. "
                "Reversão não suportada.",
                code="adjustment_on_paid_installment",
            )

        data = payload.model_dump(exclude_unset=True, exclude_none=True)

        new_due_date = data.get("due_date")
        if new_due_date:
            prev = (
                Installment.objects.for_tenant(company)
                .filter(
                    expense=instance.expense,
                    installment_number__lt=instance.installment_number,
                )
                .order_by("-installment_number")
                .first()
            )
            if prev and new_due_date < prev.due_date:
                raise BusinessRuleViolation(
                    detail=(
                        "A data de vencimento não pode ser anterior à "
                        f"parcela #{prev.installment_number} ({prev.due_date})."
                    ),
                    code="due_date_before_previous_installment",
                )

            nxt = (
                Installment.objects.for_tenant(company)
                .filter(
                    expense=instance.expense,
                    installment_number__gt=instance.installment_number,
                )
                .order_by("installment_number")
                .first()
            )
            if nxt and new_due_date > nxt.due_date:
                raise BusinessRuleViolation(
                    detail=(
                        "A data de vencimento não pode ser posterior à "
                        f"parcela #{nxt.installment_number} ({nxt.due_date})."
                    ),
                    code="due_date_after_next_installment",
                )

        for field, value in data.items():
            setattr(instance, field, value)

        instance.save()

        try:
            instance.expense.full_clean()
        except DjangoValidationError as e:
            logger.exception(
                f"Ajuste de parcela quebrou Tolerância Zero na despesa "
                f"uuid={instance.expense.uuid}"
            )
            raise BusinessRuleViolation(
                detail="O ajuste desta parcela viola as regras matemáticas da "
                "despesa (ADR-010).",
                code="expense_math_violation",
            ) from e

        logger.info(f"Parcela uuid={instance.uuid} ajustada com sucesso.")
        return instance

    @staticmethod
    @transaction.atomic
    def delete(company: Company, instance: Installment) -> None:
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        logger.info(
            f"Tentativa de deleção da Parcela uuid={instance.uuid} "
            f"por company_id={company.id}"
        )
        expense = instance.expense

        try:
            _delete_payment_event_for_single(company, instance)

            instance.delete()

            expense.full_clean()

            logger.warning(
                f"Parcela uuid={instance.uuid} DESTRUÍDA por company_id={company.id}"
            )

        except DjangoValidationError as e:
            logger.exception(
                f"Deleção de parcela quebrou integridade matemática da despesa "
                f"uuid={expense.uuid}"
            )
            raise DomainIntegrityError(
                detail=(
                    "Não é possível apagar esta parcela isoladamente pois isso "
                    "quebra a soma exata da despesa (ADR-010). Ajuste as "
                    "outras parcelas ou a despesa simultaneamente."
                ),
                code="installment_deletion_math_error",
            ) from e


@transaction.atomic
def _delete_payment_events_for_expense(company: Company, expense: Expense) -> None:
    """Remove todos os eventos PAYMENT do scheduler vinculados a esta despesa."""
    from apps.scheduler.models import Event as SchedulerEvent

    SchedulerEvent.objects.for_tenant(company).filter(
        wedding=expense.wedding,
        event_type="pagamento",
        source_installment__expense=expense,
    ).delete()


@transaction.atomic
def _delete_payment_event_for_single(company: Company, instance: Installment) -> None:
    """Remove o evento PAYMENT vinculado a uma parcela específica."""
    from apps.scheduler.models import Event as SchedulerEvent

    SchedulerEvent.objects.for_tenant(company).filter(
        wedding=instance.expense.wedding,
        event_type="pagamento",
        source_installment=instance,
    ).delete()


@transaction.atomic
def _create_payment_events(
    company: Company,
    expense: Expense,
    installments: list[Installment],
) -> None:
    """
    Cria eventos PAYMENT no scheduler para cada parcela gerada.

    Importação lazy do EventService para evitar circular imports.
    Ref: BR-S01 — Eventos PAYMENT são read-only no calendário.
    """
    from datetime import datetime, time

    from django.utils import timezone

    from apps.scheduler.services import EventService

    for inst in installments:
        naive_start = datetime.combine(inst.due_date, time(hour=9, minute=0))
        event_start = timezone.make_aware(naive_start)
        EventService.create(
            company,
            {
                "wedding": expense.wedding,
                "title": (
                    f"Pagamento: {expense.name} - Parcela "
                    f"{inst.installment_number}/{len(installments)}"
                ),
                "event_type": "pagamento",
                "start_time": event_start,
                "description": (f"Valor: R$ {inst.amount:.2f} — {expense.name}"),
                "source_installment": inst,
            },
            _caller_internal=True,
        )
