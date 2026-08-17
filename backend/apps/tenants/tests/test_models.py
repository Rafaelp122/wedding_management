"""
Testes para TenantModel (abstrato) e Company — estrutura de dados multitenant.

Verifica configuração de FK, índices, validação de fábricas e
representação textual dos modelos.
"""

from typing import cast

import pytest
from django.db import models

from apps.tenants.managers import TenantQuerySet
from apps.tenants.models import Company, TenantModel
from apps.weddings.models import Wedding

from .factories import CompanyFactory as _CompanyFactory


def CompanyFactory(**kwargs: object) -> Company:
    return cast(Company, _CompanyFactory(**kwargs))


@pytest.mark.django_db
class TestTenantModelStructure:
    def test_has_company_foreign_key(self) -> None:
        field = TenantModel._meta.get_field("company")
        assert isinstance(field, models.ForeignKey)
        assert field.remote_field.model == Company
        assert field.remote_field.on_delete == models.CASCADE

    def test_has_composite_index_on_company_and_uuid(self) -> None:
        indexes = TenantModel._meta.indexes
        index_fields = [tuple(idx.fields) for idx in indexes]

        assert ("company", "uuid") in index_fields

    def test_concrete_model_inherits_tenant_manager(self) -> None:
        assert hasattr(Wedding.objects, "for_tenant")
        assert issubclass(Wedding.objects.all().__class__, TenantQuerySet)


class TestCompanyModel:
    def test_str_returns_name(self) -> None:
        company = Company(name="Empresa Teste", slug="empresa-teste")
        assert str(company) == "Empresa Teste"

    def test_fields_configuration(self) -> None:
        name_field = Company._meta.get_field("name")
        assert name_field.max_length == 255

        slug_field = Company._meta.get_field("slug")
        assert slug_field.unique is True

        active_field = Company._meta.get_field("is_active")
        assert active_field.default is True

    def test_meta_configuration(self) -> None:
        assert Company._meta.db_table == "companies"
        assert Company._meta.ordering == ["name"]
        assert Company._meta.verbose_name == "Empresa"
        assert Company._meta.verbose_name_plural == "Empresas"

    @pytest.mark.django_db
    def test_company_inherits_from_base_model(self) -> None:
        company = CompanyFactory()
        assert company.uuid is not None
        assert company.created_at is not None
        assert company.updated_at is not None


@pytest.mark.django_db
class TestCompanyFactory:
    def test_creates_valid_company(self) -> None:
        company = CompanyFactory()
        assert company.pk is not None
        assert company.name
        assert company.slug
        assert company.is_active is True

    def test_name_can_be_overridden(self) -> None:
        company = CompanyFactory(name="Minha Empresa")
        assert company.name == "Minha Empresa"

    def test_slug_is_unique_across_instances(self) -> None:
        c1 = CompanyFactory()
        c2 = CompanyFactory()
        assert c1.slug != c2.slug
