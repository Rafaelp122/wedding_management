from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.core.shortcuts import get_object_or_404_for_tenant, resolve_tenant_resource
from apps.core.tenant import validate_tenant_ownership
from apps.tenants.models import Company
from apps.tenants.tests.factories import CompanyFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory


def _company() -> Company:
    return cast(Company, CompanyFactory())


def _wedding(**kwargs: Any) -> Wedding:
    return cast(Wedding, WeddingFactory(**kwargs))


@pytest.mark.django_db
class TestShortcuts:
    def test_get_object_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = get_object_or_404_for_tenant(Wedding, company, wedding.uuid)
        assert result == wedding

    def test_get_object_wrong_tenant(self) -> None:
        company_a = _company()
        company_b = _company()
        wedding_a = _wedding(company=company_a)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            get_object_or_404_for_tenant(Wedding, company_b, wedding_a.uuid)

        assert "não encontrado" in str(exc_info.value).lower()
        assert exc_info.value.code == "not_found_or_denied"

    def test_get_object_not_exists(self) -> None:
        company = _company()

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, uuid4())

    def test_get_object_invalid_uuid(self) -> None:
        company = _company()

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, "invalid-uuid")

    def test_get_object_select_related(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = get_object_or_404_for_tenant(
            Wedding, company, wedding.uuid, select_related=["company"]
        )
        assert result == wedding
        assert "company" in result._state.fields_cache

    def test_resolve_tenant_resource_with_uuid_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = resolve_tenant_resource(Wedding, company, wedding.uuid)

        assert result == wedding

    def test_resolve_tenant_resource_with_string_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = resolve_tenant_resource(Wedding, company, str(wedding.uuid))

        assert result == wedding

    def test_resolve_tenant_resource_with_valid_instance_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = resolve_tenant_resource(Wedding, company, wedding)

        assert result == wedding

    def test_resolve_tenant_resource_with_cross_tenant_instance_raises_error(
        self,
    ) -> None:
        company_a = _company()
        company_b = _company()
        wedding = _wedding(company=company_a)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            resolve_tenant_resource(
                Wedding,
                company_b,
                wedding,
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )

        assert exc_info.value.detail == "Casamento não encontrado ou acesso negado."
        assert exc_info.value.code == "wedding_not_found_or_denied"

    def test_resolve_tenant_resource_with_invalid_type_raises_error(self) -> None:
        company = _company()
        invalid_resource: Any = object()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            resolve_tenant_resource(
                Wedding,
                company,
                invalid_resource,
                detail="Casamento inválido ou acesso negado.",
                code="wedding_not_found_or_denied",
            )

        assert exc_info.value.detail == "Casamento inválido ou acesso negado."
        assert exc_info.value.code == "wedding_not_found_or_denied"

    def test_resolve_tenant_resource_with_select_related_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = resolve_tenant_resource(
            Wedding,
            company,
            wedding.uuid,
            select_related=["company"],
        )

        assert result == wedding
        assert "company" in result._state.fields_cache

    def test_resolve_tenant_resource_with_custom_lookup_field_success(self) -> None:
        company = _company()
        wedding = _wedding(company=company, groom_name="Rafael")

        result = resolve_tenant_resource(
            Wedding,
            company,
            "Rafael",
            lookup_field="groom_name",
            select_related=["company"],
        )

        assert result == wedding
        assert "company" in result._state.fields_cache

    def test_resolve_tenant_resource_with_custom_lookup_field_not_found(self) -> None:
        company = _company()

        with pytest.raises(ObjectNotFoundError) as exc_info:
            resolve_tenant_resource(
                Wedding,
                company,
                "Nome inexistente",
                lookup_field="groom_name",
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )

        assert exc_info.value.detail == "Casamento não encontrado ou acesso negado."
        assert exc_info.value.code == "wedding_not_found_or_denied"


@pytest.mark.django_db
class TestValidateTenantOwnership:
    def test_validate_tenant_ownership_returns_instance_for_same_tenant(self) -> None:
        company = _company()
        wedding = _wedding(company=company)

        result = validate_tenant_ownership(company, wedding)

        assert result is wedding

    def test_validate_tenant_ownership_raises_not_found_for_other_tenant(self) -> None:
        company = _company()
        other_company = _company()
        wedding = _wedding(company=other_company)

        with pytest.raises(ObjectNotFoundError) as exc_info:
            validate_tenant_ownership(
                company,
                wedding,
                detail="Casamento não encontrado ou acesso negado.",
                code="wedding_not_found_or_denied",
            )

        assert exc_info.value.detail == "Casamento não encontrado ou acesso negado."
        assert exc_info.value.code == "wedding_not_found_or_denied"
