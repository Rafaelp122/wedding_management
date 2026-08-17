"""
Testes para os seletores do domínio de Tenants.
"""

from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.tenants.models import Company
from apps.tenants.selectors import company_get_selector
from apps.tenants.tests.factories import CompanyFactory as _CompanyFactory


def CompanyFactory(*args: Any, **kwargs: Any) -> Company:
    return cast(Company, _CompanyFactory(*args, **kwargs))


@pytest.mark.django_db
class TestCompanyGetSelector:
    """Testes para o seletor company_get_selector."""

    def test_get_by_uuid_instance_success(self) -> None:
        company = CompanyFactory()
        result = company_get_selector(uuid=company.uuid)
        assert result.id == company.id
        assert result.uuid == company.uuid

    def test_get_by_uuid_string_success(self) -> None:
        company = CompanyFactory()
        result = company_get_selector(uuid=str(company.uuid))
        assert result.id == company.id
        assert result.uuid == company.uuid

    def test_get_by_uuid_not_found_raises_object_not_found(self) -> None:
        with pytest.raises(ObjectNotFoundError):
            company_get_selector(uuid=uuid4())
