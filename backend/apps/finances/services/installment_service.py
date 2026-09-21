from __future__ import annotations

import logging
from datetime import date

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from apps.core.exceptions import (
    BusinessRuleViolation,
    DomainIntegrityError,
)
from apps.core.shortcuts import resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.finances.models import Expense, Installment
from apps.finances.schemas import InstallmentAdjustIn, InstallmentIn, InstallmentPatchIn
from apps.scheduler.interfaces import (
    create_payment_events_for_installments,
    delete_payment_event_for_installment,
    delete_payment_events_for_expense,
)
from apps.tenants.models import Company


logger = logging.getLogger(__name__)


class InstallmentService:
    """Camada de serviço para mutações e orquestração de Parcelas.

    Garante o isolamento multitenant e a integridade da Tolerância Zero (ADR-010)
    nas despesas pai.

    Regras de Negócio e SSOT:
    - BR-F01 (Tolerância Zero Centesimal):
      docs/architecture/business-rules/finances/financial-integrity-rules.md
    - BR-F05 (Vencimento e Máquina de Estados de Parcelas):
      docs/architecture/business-rules/finances/installment-overdue-logic.md
    - BR-S01-SYNC (Integração de Pagamentos com Agenda):
      docs/architecture/business-rules/finances/payment-schedule-integration.md
    - Hub do Domínio Financeiro:
      docs/architecture/domains/finances-domain.md
    """

    @staticmethod
    @transaction.atomic
    def auto_generate_installments(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date,
    ) -> list[Installment]:
        """Gera parcelas de despesa com ajuste na última (Tolerância Zero).

        Para cada parcela gerada, cria um evento PAYMENT no scheduler (BR-S01)
        para visualização dos compromissos de pagamento no calendário.

        Args:
            company: O tenant atual para isolamento de dados.
            expense: A despesa pai que receberá o parcelamento.
            num_installments: Número total de parcelas (> 0).
            first_due_date: Data de vencimento da primeira parcela.

        Returns:
            list[Installment]: Lista com as instâncias de parcelas salvas no
                banco.

        Raises:
            BusinessRuleViolation: Se a despesa já possuir parcelas, se o
                número de parcelas for <= 0, ou se o valor total da despesa for
                inválido.
        """

        # Bloqueio preventivo contra reentrada e duplicação de parcelas na despesa.
        if expense.installments.exists():
            raise BusinessRuleViolation(
                detail=(
                    "Esta despesa já possui parcelas geradas. Remova-as "
                    "antes de gerar novas."
                ),
                code="installments_already_exist",
            )

        splits = expense.calculate_installment_splits(num_installments, first_due_date)
        installments: list[Installment] = [
            Installment(
                company=company,
                wedding=expense.wedding,
                expense=expense,
                installment_number=num,
                amount=amt,
                due_date=due,
                status=Installment.StatusChoices.PENDING,
            )
            for num, amt, due in splits
        ]

        # Usar .save() em vez de bulk_create para garantir que full_clean()
        # e hooks do BaseModel/Tolerância Zero sejam executados (ADR-011)
        for inst in installments:
            inst.save()

        # ── Auto-geração de Eventos PAYMENT (BR-S01) ──────────────────────
        create_payment_events_for_installments(
            company=company, expense=expense, installments=installments
        )

        return installments

    @staticmethod
    @transaction.atomic
    def redistribute(
        company: Company,
        expense: Expense,
        num_installments: int,
        first_due_date: date,
    ) -> list[Installment]:
        """Redistribui as parcelas de uma despesa.

        Remove as parcelas anteriores (e seus respectivos eventos de pagamento)
        e gera novas parcelas com novos valores e datas.

        Args:
            company: O tenant atual para isolamento de dados.
            expense: A despesa associada que terá as parcelas redistribuídas.
            num_installments: Novo número total de parcelas.
            first_due_date: Data de vencimento da primeira parcela.

        Returns:
            list[Installment]: Lista com as novas parcelas geradas.

        Raises:
            BusinessRuleViolation: Se existirem parcelas já pagas (status PAID)
                na despesa.
        """
        if expense.has_paid_installments:
            raise BusinessRuleViolation(
                detail=(
                    "Não é possível alterar o número de parcelas — existem "
                    "parcelas já marcadas como pagas. Crie uma nova despesa."
                ),
                code="redistribute_blocked_by_paid",
            )

        delete_payment_events_for_expense(company=company, expense=expense)
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
        """Cria uma parcela individual avulsa.

        Valida se a adição da nova parcela respeita a integridade matemática
        da despesa (Tolerância Zero / ADR-010).

        Args:
            company: O tenant atual para isolamento de dados.
            payload: Dados de entrada para a criação da parcela.

        Returns:
            Installment: A parcela criada.

        Raises:
            ObjectNotFoundError: Se a despesa correspondente não for encontrada.
            BusinessRuleViolation: Se a criação violar o total da despesa pai.
        """
        logger.info(f"Iniciando criação de Parcela para company_id={company.id}")

        data = payload.model_dump(exclude_unset=True)

        expense_input = data.pop("expense", None)
        expense = resolve_tenant_resource(
            Expense,
            company,
            expense_input,
            detail="Despesa não encontrada ou acesso negado.",
            code="expense_not_found_or_denied",
        )

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
        """Atualiza os dados de uma parcela.

        Revalida se as alterações mantêm a consistência matemática da despesa
        pai.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da parcela a ser atualizada.
            payload: Dados parciais de atualização da parcela.

        Returns:
            Installment: A instância da parcela atualizada.

        Raises:
            BusinessRuleViolation: Se a alteração violar a regra Tolerância
                Zero.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        logger.info(
            f"Atualizando Parcela uuid={instance.uuid} por company_id={company.id}"
        )

        updated_fields: set[str] = set()
        data = payload.model_dump(exclude_unset=True)
        protected_fields = {"amount", "due_date", "installment_number"}
        changed_protected_fields = {
            field
            for field in protected_fields & data.keys()
            if data[field] != getattr(instance, field)
        }
        if (
            instance.status == Installment.StatusChoices.PAID
            and changed_protected_fields
        ):
            raise BusinessRuleViolation(
                detail=(
                    "Parcelas pagas não podem ter valor, vencimento ou número "
                    "alterados. Faça a reversão antes de ajustar."
                ),
                code="paid_installment_immutable",
            )

        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            updated_fields.add("updated_at")
            instance.save(update_fields=list(updated_fields))

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
        """Marca uma parcela como paga.

        Garante a atualização de status para PAID e define a data de pagamento
        como o dia corrente, revalidando a despesa pai.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da parcela a ser paga.

        Returns:
            Installment: A parcela atualizada.

        Raises:
            BusinessRuleViolation: Se a parcela já estiver paga ou se a
                transação violar a consistência matemática da despesa.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        instance.mark_as_paid(paid_date=date.today())
        instance.save(update_fields=["status", "paid_date", "updated_at"])

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
        """Desmarca uma parcela que foi definida como paga.

        Remove a data de pagamento e redefine o status apropriado dependendo
        da data de vencimento (PENDING ou OVERDUE).

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da parcela a ser revertida.

        Returns:
            Installment: A parcela com status atualizado.

        Raises:
            BusinessRuleViolation: Se a parcela não estiver paga ou violar as
                regras matemáticas da despesa pai.
        """
        validate_tenant_ownership(
            company,
            instance,
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
        instance.unmark_as_paid()
        instance.save(update_fields=["status", "paid_date", "updated_at"])

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
        """Ajusta o valor ou data de vencimento de uma parcela.

        Garante que a nova data de vencimento respeite a sequência cronológica
        das parcelas anterior e posterior, além de revalidar a despesa pai.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da parcela a ser ajustada.
            payload: Dados de ajuste da parcela.

        Returns:
            Installment: A instância da parcela ajustada.

        Raises:
            BusinessRuleViolation: Se a parcela estiver paga, se a data estiver
                fora da cronologia sequencial ou se violar a soma da despesa pai.
        """
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
            instance.validate_chronology(new_due_date)

        updated_fields: set[str] = set()
        for field, value in data.items():
            setattr(instance, field, value)
            updated_fields.add(field)

        if updated_fields:
            instance.save(update_fields=list(updated_fields | {"updated_at"}))

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
        """Exclui uma parcela individual.

        Remove o evento de pagamento associado no scheduler e revalida a
        despesa pai.

        Args:
            company: O tenant atual para isolamento de dados.
            instance: A instância da parcela a ser excluída.

        Raises:
            DomainIntegrityError: Se a exclusão violar a integridade
                matemática da despesa pai.
        """
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
            delete_payment_event_for_installment(company=company, installment=instance)

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

    @staticmethod
    @transaction.atomic
    def mark_overdue_installments(
        company: Company | None = None,
        today: date | None = None,
    ) -> int:
        """Marca como OVERDUE todas as parcelas PENDING com due_date anterior a hoje

        e dispara a criação de Notificações In-App para os usuários da empresa.

        Args:
            company: Tenant opcional para restrição de escopo.
            today: Data de referência para checagem de vencimento (opcional).

        Returns:
            int: Quantidade de parcelas atualizadas para OVERDUE.
        """
        if today is None:
            today = date.today()

        qs = Installment.objects.filter(
            status=Installment.StatusChoices.PENDING,
            due_date__lt=today,
        )
        if company is not None:
            qs = qs.filter(company=company)

        pending_overdue = list(
            qs.select_related(
                "company", "expense", "expense__wedding"
            ).prefetch_related("company__users")
        )

        if not pending_overdue:
            return 0

        count = 0
        from apps.notifications.interfaces import notify_installment_overdue

        for inst in pending_overdue:
            inst.mark_as_overdue()
            inst.save(update_fields=["status", "updated_at"])
            count += 1

            users = [u for u in inst.company.users.all() if u.is_active]
            wedding = inst.expense.wedding if inst.expense else None
            wedding_name = (
                f"Casamento de {wedding.bride_name} e {wedding.groom_name}"
                if wedding
                else None
            )

            notify_installment_overdue(
                company=inst.company,
                installment_uuid=inst.expense.uuid if inst.expense else inst.uuid,
                expense_name=inst.expense.name if inst.expense else "Despesa",
                installment_number=inst.installment_number,
                amount=inst.amount,
                due_date=inst.due_date,
                wedding_uuid=wedding.uuid if wedding else None,
                wedding_name=wedding_name,
                users=users,
            )

        return count
