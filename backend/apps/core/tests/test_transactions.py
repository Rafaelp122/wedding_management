"""
Testes de integridade transacional e rollback atômico.

Garante que falhas ocorridas durante operações em múltiplos registros
sejam completamente revertidas via transaction.atomic, assegurando que
nenhum registro parcial ou órfão permaneça no banco de dados.
"""

from decimal import Decimal
from typing import cast
from unittest.mock import patch

import pytest
from django.db import transaction

from apps.finances.models import BudgetCategory, Expense, Installment
from apps.finances.schemas import ExpenseIn
from apps.finances.services.expense_service import ExpenseService
from apps.finances.tests.factories import BudgetCategoryFactory
from apps.logistics.models import Contract, Supplier
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.scheduler.models import Event
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestTransactionRollback:
    """Suíte de testes para validação de rollback atômico em operações complexas."""

    def test_expense_creation_rollback_on_installment_failure(self) -> None:
        """
        Garante rollback completo ao criar despesa se a geração de parcelas falhar.

        Quando a geração de parcelas lança uma exceção, o decorator @transaction.atomic
        no ExpenseService.create deve reverter a inserção da despesa, mantendo 0
        registros no banco de dados.
        """
        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=company, wedding=wedding),
        )

        payload = ExpenseIn(
            category=category.uuid,
            name="Buffet Principal",
            description="Pagamento do buffet",
            actual_amount=Decimal("12000.00"),
            estimated_amount=Decimal("12000.00"),
            num_installments=3,
        )

        with patch(
            "apps.finances.services.installment_service."
            "InstallmentService.auto_generate_installments",
            side_effect=RuntimeError("Simulação de falha na geração de parcelas"),
        ):
            with pytest.raises(RuntimeError, match="Simulação de falha"):
                ExpenseService.create(company=company, payload=payload)

        assert Expense.objects.filter(company=company).count() == 0
        assert Installment.objects.filter(company=company).count() == 0
        assert Event.objects.filter(company=company).count() == 0

    def test_expense_creation_rollback_on_event_creation_failure(self) -> None:
        """
        Garante rollback completo quando a geração de eventos de agendamento falha.

        Se a criação de parcelas ocorrer mas a auto-geração de eventos de pagamento
        (BR-S01) falhar, a transação inteira é revertida (0 despesas/parcelas/eventos).
        """
        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=company, wedding=wedding),
        )

        payload = ExpenseIn(
            category=category.uuid,
            name="Decoração Floral",
            description="Flores da cerimônia",
            actual_amount=Decimal("5000.00"),
            estimated_amount=Decimal("5000.00"),
            num_installments=2,
        )

        with patch(
            "apps.finances.services.installment_service._create_payment_events",
            side_effect=ValueError("Simulação de falha no serviço de agendamento"),
        ):
            with pytest.raises(ValueError, match="Simulação de falha"):
                ExpenseService.create(company=company, payload=payload)

        assert Expense.objects.filter(company=company).count() == 0
        assert Installment.objects.filter(company=company).count() == 0
        assert Event.objects.filter(company=company).count() == 0

    def test_multi_model_transaction_rollback_leaves_zero_orphans(self) -> None:
        """
        Simula exceção no meio de um fluxo transacional envolvendo 4 modelos.

        Verifica que nenhum registro parcial (Supplier, Contract, Expense ou
        Installment) permanece persistido caso o processo seja interrompido no meio.
        """
        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=company, wedding=wedding),
        )

        initial_suppliers = Supplier.objects.count()
        initial_contracts = Contract.objects.count()
        initial_expenses = Expense.objects.count()
        initial_installments = Installment.objects.count()

        with pytest.raises(RuntimeError, match="Falha no pipeline de contrato"):
            with transaction.atomic():
                supplier = cast(
                    Supplier,
                    SupplierFactory(company=company, name="Fornecedor Orfao"),
                )
                ContractFactory(company=company, wedding=wedding, supplier=supplier)

                ExpenseService.create(
                    company=company,
                    payload=ExpenseIn(
                        category=category.uuid,
                        name="Despesa Cancelada",
                        actual_amount=Decimal("3000.00"),
                        estimated_amount=Decimal("3000.00"),
                        num_installments=3,
                    ),
                )

                raise RuntimeError("Falha no pipeline de contrato")

        assert Supplier.objects.count() == initial_suppliers
        assert Contract.objects.count() == initial_contracts
        assert Expense.objects.count() == initial_expenses
        assert Installment.objects.count() == initial_installments

    def test_redistribute_installments_rollback_on_error(self) -> None:
        """
        Garante que a falha ao redistribuir parcelas não destrói as parcelas existentes.

        O método InstallmentService.redistribute deve reverter a deleção das parcelas
        originais caso ocorra um erro durante a recriação.
        """
        from apps.finances.services.installment_service import InstallmentService

        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        category = cast(
            BudgetCategory,
            BudgetCategoryFactory(company=company, wedding=wedding),
        )

        expense = ExpenseService.create(
            company=company,
            payload=ExpenseIn(
                category=category.uuid,
                name="Som e Iluminação",
                actual_amount=Decimal("4000.00"),
                estimated_amount=Decimal("4000.00"),
                num_installments=2,
            ),
        )

        initial_installment_ids = set(expense.installments.values_list("id", flat=True))
        assert len(initial_installment_ids) == 2

        with patch(
            "apps.finances.services.installment_service."
            "InstallmentService.auto_generate_installments",
            side_effect=RuntimeError("Erro ao auto-gerar parcelas"),
        ):
            with pytest.raises(RuntimeError, match="Erro ao auto-gerar parcelas"):
                InstallmentService.redistribute(
                    company=company,
                    expense=expense,
                    num_installments=4,
                    first_due_date=expense.installments.first().due_date,  # type: ignore[union-attr]
                )

        current_installment_ids = set(expense.installments.values_list("id", flat=True))
        assert current_installment_ids == initial_installment_ids
