from typing import no_type_check
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.core.tenant import validate_tenant_ownership
from apps.core.tests.factories import WeddingFactory
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.models import Wedding


@pytest.mark.django_db
class TestShortcuts:
    def test_get_object_success(self):
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        result = get_object_or_404_for_tenant(Wedding, company, wedding.uuid)
        assert result == wedding

    def test_get_object_wrong_tenant(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_a = WeddingFactory(company=company_a)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            get_object_or_404_for_tenant(Wedding, company_b, wedding_a.uuid)

        assert "não encontrado" in str(exc_info.value).lower()
        assert exc_info.value.code == "not_found_or_denied"

    def test_get_object_not_exists(self):
        company = CompanyFactory()

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, uuid4())

    def test_get_object_invalid_uuid(self):
        company = CompanyFactory()

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, "invalid-uuid")

    def test_get_object_select_related(self):
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        # Apenas para verificar se não explode e chama o método
        result = get_object_or_404_for_tenant(
            Wedding, company, wedding.uuid, select_related=["company"]
        )
        assert result == wedding


@pytest.mark.django_db
class TestValidateTenantOwnership:
    @no_type_check
    def test_validate_tenant_ownership_returns_instance_for_same_tenant(self) -> None:
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        result = validate_tenant_ownership(company, wedding)

        assert result is wedding

    @no_type_check
    def test_validate_tenant_ownership_raises_not_found_for_other_tenant(self) -> None:
        company = CompanyFactory()
        other_company = CompanyFactory()
        wedding = WeddingFactory(company=other_company)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            validate_tenant_ownership(
                company,
                wedding,
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )

        assert exc_info.value.detail == "Casamento não encontrado ou acesso negado."
        assert exc_info.value.code == "wedding_not_found_or_denied"
