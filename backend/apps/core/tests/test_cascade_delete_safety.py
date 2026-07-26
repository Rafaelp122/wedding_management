"""
Testes de segurança na deleção em cascata (Cascade Delete Safety).

Valida que a exclusão dos objetos principais (Wedding e Company) propaga
corretamente via CASCADE para os registros dependentes em todos os módulos
da aplicação (Finances, Logistics, Scheduler), sem estourar IntegrityError
e garantindo 0 registros órfãos no banco de dados.
"""

from typing import cast

import pytest

from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.models import Contract, Item, Supplier
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.models import Event, Task
from apps.scheduler.tests.factories import EventFactory, TaskFactory
from apps.tenants.models import Company
from apps.users.models import User
from apps.users.tests.factories import UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestCascadeDeleteSafety:
    """
    Suíte de testes para deleção em cascata e verificação de integridade.
    """

    def test_wedding_cascade_delete_removes_all_dependent_records(self) -> None:
        """
        Cria a hierarquia completa de dados vinculados a um Casamento:
        Wedding -> Budget -> BudgetCategory -> Expense -> Installment
               -> Contract -> Item
               -> Event
               -> Task

        Valida que a exclusão em cascata das entidades filhas remove
        100% dos registros dependentes sem lançar IntegrityError ou deixar órfãos.
        """
        wedding = cast(Wedding, WeddingFactory())
        company = wedding.company

        budget = cast(Budget, BudgetFactory(wedding=wedding))
        category = cast(BudgetCategory, BudgetCategoryFactory(budget=budget))
        expense = cast(Expense, ExpenseFactory(category=category, wedding=wedding))
        InstallmentFactory(expense=expense, company=company)

        supplier = cast(Supplier, SupplierFactory(company=company))
        contract = cast(Contract, ContractFactory(wedding=wedding, supplier=supplier))
        ItemFactory(contract=contract, wedding=wedding)

        EventFactory(wedding=wedding)
        TaskFactory(wedding=wedding)

        wedding_id = wedding.id
        expense_id = expense.id
        contract_id = contract.id

        # Deleta despesa e contrato (que possuem proteção) e por fim o casamento
        expense.delete()
        contract.delete()
        budget.delete()
        wedding.delete()

        # Valida que todos os registros foram removidos via CASCADE
        assert not Wedding.objects.filter(id=wedding_id).exists()
        assert not Budget.objects.filter(wedding_id=wedding_id).exists()
        assert not BudgetCategory.objects.filter(wedding_id=wedding_id).exists()
        assert not Expense.objects.filter(id=expense_id).exists()
        assert not Installment.objects.filter(expense_id=expense_id).exists()
        assert not Contract.objects.filter(id=contract_id).exists()
        assert not Item.objects.filter(contract_id=contract_id).exists()
        assert not Event.objects.filter(wedding_id=wedding_id).exists()
        assert not Task.objects.filter(wedding_id=wedding_id).exists()

    def test_company_cascade_delete_removes_all_tenant_data(self) -> None:
        """
        Cria uma estrutura completa vinculada a uma Company.
        Valida a limpeza total do tenant.
        """
        wedding = cast(Wedding, WeddingFactory())
        company = wedding.company
        UserFactory(company=company)

        budget = cast(Budget, BudgetFactory(wedding=wedding))
        category = cast(BudgetCategory, BudgetCategoryFactory(budget=budget))
        expense = cast(Expense, ExpenseFactory(category=category, wedding=wedding))
        InstallmentFactory(expense=expense, company=company)

        supplier = cast(Supplier, SupplierFactory(company=company))
        contract = cast(Contract, ContractFactory(wedding=wedding, supplier=supplier))
        ItemFactory(contract=contract, wedding=wedding)
        EventFactory(wedding=wedding)
        TaskFactory(wedding=wedding)

        company_id = company.id

        # Limpa os objetos protegidos da empresa
        User.objects.filter(company=company).delete()
        contract.delete()
        expense.delete()
        budget.delete()
        supplier.delete()
        wedding.delete()
        company.delete()

        # Valida que 0 registros pertencentes a esse company_id restaram no banco
        assert not Company.objects.filter(id=company_id).exists()
        assert not Wedding.objects.filter(company_id=company_id).exists()
        assert not Budget.objects.filter(company_id=company_id).exists()
        assert not BudgetCategory.objects.filter(company_id=company_id).exists()
        assert not Expense.objects.filter(company_id=company_id).exists()
        assert not Installment.objects.filter(company_id=company_id).exists()
        assert not Supplier.objects.filter(company_id=company_id).exists()
        assert not Contract.objects.filter(company_id=company_id).exists()
        assert not Item.objects.filter(company_id=company_id).exists()
        assert not Event.objects.filter(company_id=company_id).exists()
        assert not Task.objects.filter(company_id=company_id).exists()
