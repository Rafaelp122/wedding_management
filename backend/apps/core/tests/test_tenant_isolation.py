"""
Suíte de testes de isolamento multi-tenant para os modelos principais.

Utiliza a classe base BaseTenantIsolationTest para aplicar testes parametrizados
garantindo que cada modelo de tenant filtra seus objetos via Manager (for_tenant)
e via shortcuts de busca (get_object_or_404_for_tenant).

Destaques Técnicos:
- NUNCA utiliza .objects.create() diretamente, respeitando as factories.
- Cobre modelos de weddings, finances, logistics e scheduler.
"""

from typing import Any

import factory
import pytest
from django.db import models

from apps.core.tests.base import BaseTenantIsolationTest
from apps.finances.models import Budget, BudgetCategory, Expense, Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory,
    BudgetFactory,
    ExpenseFactory,
    InstallmentFactory,
)
from apps.logistics.models import Contract, Supplier
from apps.logistics.models import Item as LogisticsItem
from apps.logistics.tests.factories import (
    ContractFactory,
    ItemFactory,
    SupplierFactory,
)
from apps.scheduler.models import Event, Task
from apps.scheduler.tests.factories import EventFactory, TaskFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestTenantIsolation(BaseTenantIsolationTest):
    """
    Testes concretos e parametrizados de isolamento multi-tenant.

    Aplica as asserções reutilizáveis da BaseTenantIsolationTest sobre os modelos
    das quatro áreas funcionais do sistema.
    """

    @pytest.mark.parametrize(
        "model_cls,factory_cls",
        [
            (Wedding, WeddingFactory),
            (Budget, BudgetFactory),
            (BudgetCategory, BudgetCategoryFactory),
            (Expense, ExpenseFactory),
            (Installment, InstallmentFactory),
            (Supplier, SupplierFactory),
            (Contract, ContractFactory),
            (LogisticsItem, ItemFactory),
            (Event, EventFactory),
            (Task, TaskFactory),
        ],
    )
    def test_model_tenant_isolation(
        self,
        model_cls: type[models.Model],
        factory_cls: type[factory.django.DjangoModelFactory[Any]],
    ) -> None:
        """
        Executa os testes de isolamento de tenant para o modelo e fábrica especificados.

        Args:
            model_cls: Classe do modelo Django sob teste.
            factory_cls: Fábrica FactoryBoy correspondente.
        """
        self.assert_tenant_isolation(model_cls, factory_cls)
