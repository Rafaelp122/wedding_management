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
from apps.tenants.tests.factories import CompanyFactory
from apps.users.models import User
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestCascadeDeleteSafety:
    """
    Suíte de testes para deleção em cascata e verificação de integridade.
    """

    def test_wedding_cascade_deletes_cascade_entities(self) -> None:
        """
        Valida que a execução direta de wedding.delete() remove em cascata
        todos os objetos vinculados com relação CASCADE.
        """
        wedding = cast(Wedding, WeddingFactory())

        budget = cast(Budget, BudgetFactory(wedding=wedding))
        category = cast(BudgetCategory, BudgetCategoryFactory(budget=budget))
        event = cast(Event, EventFactory(wedding=wedding))
        task = cast(Task, TaskFactory(wedding=wedding))

        wedding_id = wedding.id
        budget_id = budget.id
        category_id = category.id
        event_id = event.id
        task_id = task.id

        wedding.delete()

        assert not Wedding.objects.filter(id=wedding_id).exists()
        assert not Budget.objects.filter(id=budget_id).exists()
        assert not BudgetCategory.objects.filter(id=category_id).exists()
        assert not Event.objects.filter(id=event_id).exists()
        assert not Task.objects.filter(id=task_id).exists()

    def test_expense_and_contract_cascade_deletes_dependents(self) -> None:
        """
        Valida que a deleção de Expense remove Installment em cascata
        e a deleção de Contract desvincula Item (SET_NULL).
        """
        company = cast(Company, CompanyFactory())
        wedding = cast(Wedding, WeddingFactory(company=company))
        budget = cast(Budget, BudgetFactory(wedding=wedding))
        category = cast(BudgetCategory, BudgetCategoryFactory(budget=budget))

        expense = cast(Expense, ExpenseFactory(category=category, wedding=wedding))
        installment = cast(
            Installment, InstallmentFactory(expense=expense, company=company)
        )

        supplier = cast(Supplier, SupplierFactory(company=company))
        contract = cast(Contract, ContractFactory(wedding=wedding, supplier=supplier))
        item = cast(Item, ItemFactory(contract=contract, wedding=wedding))

        installment_id = installment.id

        expense.delete()
        contract.delete()

        item.refresh_from_db()

        assert not Installment.objects.filter(id=installment_id).exists()
        assert item.contract_id is None

    def test_company_cascade_delete_removes_all_tenant_data(self) -> None:
        """
        Valida que a execução direta de company.delete() remove em cascata
        todos os dados vinculados à empresa tenant após liberar PROTECTs.
        """
        wedding = cast(Wedding, WeddingFactory())
        company = wedding.company

        budget = cast(Budget, BudgetFactory(wedding=wedding))
        category = cast(BudgetCategory, BudgetCategoryFactory(budget=budget))
        supplier = cast(Supplier, SupplierFactory(company=company))

        event = cast(Event, EventFactory(wedding=wedding))
        task = cast(Task, TaskFactory(wedding=wedding))

        company_id = company.id
        wedding_id = wedding.id
        budget_id = budget.id
        category_id = category.id
        supplier_id = supplier.id
        event_id = event.id
        task_id = task.id

        User.objects.filter(company=company).delete()
        company.delete()

        assert not Company.objects.filter(id=company_id).exists()
        assert not Wedding.objects.filter(id=wedding_id).exists()
        assert not Budget.objects.filter(id=budget_id).exists()
        assert not BudgetCategory.objects.filter(id=category_id).exists()
        assert not Supplier.objects.filter(id=supplier_id).exists()
        assert not Event.objects.filter(id=event_id).exists()
        assert not Task.objects.filter(id=task_id).exists()
