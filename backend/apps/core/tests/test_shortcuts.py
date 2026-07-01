from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.core.shortcuts import get_object_or_404_for_tenant
from apps.tenants.models import Company
from apps.weddings.models import Wedding


@pytest.mark.django_db
class TestShortcuts:
    def test_get_object_success(self):
        company = Company.objects.create(name="Test Company", slug="test-company")
        wedding = Wedding.objects.create(
            company=company,
            groom_name="Groom",
            bride_name="Bride",
            date="2026-12-31",
            location="Test Location",
        )

        result = get_object_or_404_for_tenant(Wedding, company, wedding.uuid)
        assert result == wedding

    def test_get_object_wrong_tenant(self):
        company_a = Company.objects.create(name="Company A", slug="company-a")
        company_b = Company.objects.create(name="Company B", slug="company-b")
        wedding_a = Wedding.objects.create(
            company=company_a,
            groom_name="Groom A",
            bride_name="Bride A",
            date="2026-12-31",
            location="Test Location A",
        )

        with pytest.raises(ObjectNotFoundError) as exc_info:
            get_object_or_404_for_tenant(Wedding, company_b, wedding_a.uuid)

        assert "não encontrado" in str(exc_info.value).lower()
        assert exc_info.value.code == "not_found_or_denied"

    def test_get_object_not_exists(self):
        company = Company.objects.create(name="Test Company", slug="test-company")

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, uuid4())

    def test_get_object_invalid_uuid(self):
        company = Company.objects.create(name="Test Company", slug="test-company")

        with pytest.raises(ObjectNotFoundError):
            get_object_or_404_for_tenant(Wedding, company, "invalid-uuid")

    def test_get_object_select_related(self):
        company = Company.objects.create(name="Test Company", slug="test-company")
        wedding = Wedding.objects.create(
            company=company,
            groom_name="Groom",
            bride_name="Bride",
            date="2026-12-31",
            location="Test Location",
        )

        # Apenas para verificar se não explode e chama o método
        result = get_object_or_404_for_tenant(
            Wedding, company, wedding.uuid, select_related=["company"]
        )
        assert result == wedding
