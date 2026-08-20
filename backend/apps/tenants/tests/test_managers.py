"""
Testes CRÍTICOS para TenantQuerySet e TenantManager — isolamento multitenant.

O for_tenant() é a espinha dorsal de todo o sistema.
Cada serviço depende dele para filtrar registros pela empresa correta.
"""

from typing import Any, cast

import pytest

from apps.tenants.managers import TenantQuerySet
from apps.tenants.models import TenantModel
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory

from .factories import CompanyFactory


@pytest.mark.django_db
class TestTenantQuerySet:
    def test_for_tenant_filters_by_company(self) -> None:
        company_a = cast(Any, CompanyFactory())
        company_b = cast(Any, CompanyFactory())

        w1 = cast(Any, WeddingFactory(company=company_a))
        WeddingFactory(company=company_b)
        w3 = cast(Any, WeddingFactory(company=company_a))

        qs = Wedding.objects.for_tenant(company_a)

        assert qs.count() == 2
        assert set(qs.values_list("id", flat=True)) == {w1.id, w3.id}

    def test_for_tenant_returns_empty_when_no_records(self) -> None:
        company = cast(Any, CompanyFactory())

        qs = Wedding.objects.for_tenant(company)

        assert qs.count() == 0
        assert not qs.exists()

    def test_for_tenant_excludes_other_company_records(self) -> None:
        company_a = cast(Any, CompanyFactory())
        company_b = cast(Any, CompanyFactory())

        w_a = cast(Any, WeddingFactory(company=company_a))
        w_b = cast(Any, WeddingFactory(company=company_b))

        qs = Wedding.objects.for_tenant(company_a)
        ids = set(qs.values_list("id", flat=True))

        assert w_a.id in ids
        assert w_b.id not in ids

    def test_for_tenant_with_multiple_models_isolated(self) -> None:
        company_a = cast(Any, CompanyFactory())
        company_b = cast(Any, CompanyFactory())

        WeddingFactory(company=company_a)
        WeddingFactory(company=company_b)

        assert Wedding.objects.for_tenant(company_a).count() == 1
        assert Wedding.objects.for_tenant(company_b).count() == 1


@pytest.mark.django_db
class TestTenantManager:
    def test_get_queryset_returns_tenant_queryset(self) -> None:
        qs = Wedding.objects.get_queryset()

        assert isinstance(qs, TenantQuerySet)

    def test_for_tenant_delegates_to_queryset(self) -> None:
        company = cast(Any, CompanyFactory())
        WeddingFactory(company=company)

        result = Wedding.objects.for_tenant(company)

        assert isinstance(result, TenantQuerySet)
        assert result.count() == 1

    def test_all_models_with_tenant_manager_return_same_type(self) -> None:
        """Garante consistência: todo TenantModel expõe TenantManager.

        NOTA: Ao adicionar novos modelos TenantModel, inclua-os nesta lista
        para manter o guard de regressão ativo.
        """
        from apps.finances.models import (
            Budget,
            BudgetCategory,
            Expense,
            Installment,
        )
        from apps.logistics.models import Contract, Item, Supplier
        from apps.notifications.models import Notification
        from apps.scheduler.models import Event, Task
        from apps.weddings.models import Wedding

        models_with_tenant = [
            Wedding,
            Budget,
            BudgetCategory,
            Expense,
            Installment,
            Contract,
            Item,
            Supplier,
            Event,
            Task,
            Notification,
        ]

        for model_class in models_with_tenant:
            manager = cast(Any, model_class).objects
            assert hasattr(manager, "for_tenant"), (
                f"{model_class.__name__}.objects não possui método for_tenant"
            )
            assert issubclass(manager._queryset_class, TenantQuerySet), (
                f"{model_class.__name__}.objects._queryset_class "
                "não herda de TenantQuerySet"
            )

    def test_tenant_model_is_abstract(self) -> None:
        assert TenantModel._meta.abstract is True

    def test_tenant_manager_cannot_be_accessed_on_abstract(self) -> None:
        with pytest.raises(AttributeError):
            _ = TenantModel.objects
