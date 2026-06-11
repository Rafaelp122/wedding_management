"""
Testes CRÍTICOS para TenantQuerySet e TenantManager — isolamento multitenant.

O for_tenant() é a espinha dorsal de todo o sistema.
Cada serviço depende dele para filtrar registros pela empresa correta.
"""

import pytest

from apps.tenants.managers import TenantManager, TenantQuerySet
from apps.tenants.models import TenantModel
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory

from .factories import CompanyFactory


@pytest.mark.django_db
class TestTenantQuerySet:
    def test_for_tenant_filters_by_company(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()

        w1 = WeddingFactory(company=company_a)
        WeddingFactory(company=company_b)
        w3 = WeddingFactory(company=company_a)

        qs = Wedding.objects.for_tenant(company_a)

        assert qs.count() == 2
        assert set(qs.values_list("id", flat=True)) == {w1.id, w3.id}

    def test_for_tenant_returns_empty_when_no_records(self):
        company = CompanyFactory()

        qs = Wedding.objects.for_tenant(company)

        assert qs.count() == 0
        assert not qs.exists()

    def test_for_tenant_excludes_other_company_records(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()

        w_a = WeddingFactory(company=company_a)
        w_b = WeddingFactory(company=company_b)

        qs = Wedding.objects.for_tenant(company_a)
        ids = set(qs.values_list("id", flat=True))

        assert w_a.id in ids
        assert w_b.id not in ids

    def test_for_tenant_with_multiple_models_isolated(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()

        WeddingFactory(company=company_a)
        WeddingFactory(company=company_b)

        assert Wedding.objects.for_tenant(company_a).count() == 1
        assert Wedding.objects.for_tenant(company_b).count() == 1


@pytest.mark.django_db
class TestTenantManager:
    def test_get_queryset_returns_tenant_queryset(self):
        qs = Wedding.objects.get_queryset()

        assert isinstance(qs, TenantQuerySet)

    def test_for_tenant_delegates_to_queryset(self):
        company = CompanyFactory()
        WeddingFactory(company=company)

        result = Wedding.objects.for_tenant(company)

        assert isinstance(result, TenantQuerySet)
        assert result.count() == 1

    def test_all_models_with_tenant_manager_return_same_type(self):
        """Garante consistência: todo TenantModel expõe TenantManager."""
        models_with_tenant = [Wedding]

        for model_class in models_with_tenant:
            assert isinstance(model_class.objects, TenantManager), (
                f"{model_class.__name__}.objects não é TenantManager"
            )

    def test_tenant_model_is_abstract(self):
        assert TenantModel._meta.abstract is True

    def test_tenant_manager_cannot_be_accessed_on_abstract(self):
        with pytest.raises(AttributeError):
            _ = TenantModel.objects
