"""
Testes para o comando mark_overdue_installments.

Verifica se o comando marca corretamente as parcelas pendentes e vencidas como OVERDUE,
respeitando o estado de pagamento, datas futuras e isolamento de multi-tenancy.
"""

import io
import logging
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.management import call_command

from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.tests.factories import WeddingFactory


def _create_installment(company, status, due_date, amount=Decimal("100.00"), **kwargs):
    """
    Helper para criar parcelas com status e vencimento específicos por empresa.

    Args:
        company: A empresa associada ao casamento/despesa.
        status: Status inicial da parcela.
        due_date: Data de vencimento da parcela.
        amount: Valor monetário da parcela.
        **kwargs: Outros argumentos passados ao InstallmentFactory.

    Returns:
        Instância de Installment criada no banco.
    """
    wedding = WeddingFactory(company=company)
    budget = BudgetFactory(wedding=wedding)
    category = BudgetCategoryFactory(budget=budget, wedding=wedding)
    expense = ExpenseFactory(
        wedding=wedding, category=category, contract=None, actual_amount=amount
    )
    return InstallmentFactory(
        expense=expense,
        status=status,
        due_date=due_date,
        amount=amount,
        **kwargs,
    )


@pytest.mark.django_db
class TestMarkOverdueInstallmentsCommand:
    """Testes do comando Django mark_overdue_installments."""

    def test_mark_overdue_success(self, user):
        """
        Verifica que parcelas PENDING com due_date menor que hoje mudam para OVERDUE.
        """
        today = date.today()
        # Parcela vencida ontem
        inst1 = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today - timedelta(days=1),
        )
        # Parcela vencida há 5 dias
        inst2 = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today - timedelta(days=5),
        )

        out = io.StringIO()
        call_command("mark_overdue_installments", stdout=out)

        inst1.refresh_from_db()
        inst2.refresh_from_db()

        assert inst1.status == Installment.StatusChoices.OVERDUE
        assert inst2.status == Installment.StatusChoices.OVERDUE

        output = out.getvalue()
        assert "2 parcela(s) marcada(s) como OVERDUE" in output
        assert f"vencidas antes de {today}" in output

    def test_mark_overdue_paid_not_changed(self, user):
        """
        Verifica que parcelas PAID com due_date menor que hoje não são alteradas.
        """
        today = date.today()
        # Parcela vencida ontem mas já paga
        inst = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PAID,
            due_date=today - timedelta(days=1),
            paid_date=today - timedelta(days=1),
        )

        out = io.StringIO()
        call_command("mark_overdue_installments", stdout=out)

        inst.refresh_from_db()
        assert inst.status == Installment.StatusChoices.PAID

        output = out.getvalue()
        assert "Nenhuma parcela vencida encontrada." in output

    def test_mark_overdue_pending_future_not_changed(self, user):
        """
        Verifica que parcelas PENDING com due_date >= hoje não são alteradas.
        """
        today = date.today()
        # Parcela vencendo hoje
        inst_today = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today,
        )
        # Parcela vencendo amanhã
        inst_future = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today + timedelta(days=1),
        )

        out = io.StringIO()
        call_command("mark_overdue_installments", stdout=out)

        inst_today.refresh_from_db()
        inst_future.refresh_from_db()

        assert inst_today.status == Installment.StatusChoices.PENDING
        assert inst_future.status == Installment.StatusChoices.PENDING

        output = out.getvalue()
        assert "Nenhuma parcela vencida encontrada." in output

    def test_mark_overdue_multitenancy(self, user):
        """
        Verifica o comportamento correto do comando em ambiente multi-tenancy.
        Garante que parcelas pendentes e atrasadas de qualquer tenant sejam processadas,
        enquanto parcelas pagas ou futuras de todos os tenants não sejam afetadas.
        """
        today = date.today()
        other_company = CompanyFactory()

        # Tenant 1 (user.company): parcelas
        t1_overdue_pending = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today - timedelta(days=1),
        )
        t1_future_pending = _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today + timedelta(days=1),
        )

        # Tenant 2 (other_company): parcelas
        t2_overdue_pending = _create_installment(
            company=other_company,
            status=Installment.StatusChoices.PENDING,
            due_date=today - timedelta(days=2),
        )
        t2_future_pending = _create_installment(
            company=other_company,
            status=Installment.StatusChoices.PENDING,
            due_date=today + timedelta(days=2),
        )
        t2_overdue_paid = _create_installment(
            company=other_company,
            status=Installment.StatusChoices.PAID,
            due_date=today - timedelta(days=3),
            paid_date=today - timedelta(days=3),
        )

        out = io.StringIO()
        call_command("mark_overdue_installments", stdout=out)

        # Atualiza do banco
        t1_overdue_pending.refresh_from_db()
        t1_future_pending.refresh_from_db()
        t2_overdue_pending.refresh_from_db()
        t2_future_pending.refresh_from_db()
        t2_overdue_paid.refresh_from_db()

        # Assertions
        assert t1_overdue_pending.status == Installment.StatusChoices.OVERDUE
        assert t1_future_pending.status == Installment.StatusChoices.PENDING
        assert t2_overdue_pending.status == Installment.StatusChoices.OVERDUE
        assert t2_future_pending.status == Installment.StatusChoices.PENDING
        assert t2_overdue_paid.status == Installment.StatusChoices.PAID

        output = out.getvalue()
        assert "2 parcela(s) marcada(s) como OVERDUE" in output

    def test_mark_overdue_logging(self, caplog, user):
        """
        Verifica que mensagens informativas de log são geradas apropriadamente.
        """
        today = date.today()
        _create_installment(
            company=user.company,
            status=Installment.StatusChoices.PENDING,
            due_date=today - timedelta(days=2),
        )

        # Captura os logs com nível INFO ou superior
        with caplog.at_level(logging.INFO):
            call_command("mark_overdue_installments")

        # Verifica se o logger do comando registrou a mensagem esperada
        log_messages = [record.message for record in caplog.records]
        expected_log = (
            "mark_overdue_installments: 1 parcela(s) marcada(s) como OVERDUE."
        )
        assert expected_log in log_messages
