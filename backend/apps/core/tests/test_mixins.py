"""
Testes CRÍTICOS para WeddingOwnedMixin — blindagem vertical e horizontal.

O clean() do mixin impede vazamento de dados entre tenants e entre
casamentos, garantindo isolamento multitenant completo.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import WeddingOwnedMixin
from apps.core.models import BaseModel
from apps.core.tests.factories import WeddingFactory
from apps.tenants.tests.factories import CompanyFactory


class WeddingOwnedStub(BaseModel, WeddingOwnedMixin):
    """Stub auto-contido: não depende de TenantModel de outro app."""

    company = models.ForeignKey(
        "tenants.Company", on_delete=models.CASCADE, related_name="+"
    )
    name = models.CharField(max_length=100)
    related_item = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        app_label = "core"


@pytest.mark.django_db
class TestWeddingOwnedMixinCrossTenant:
    """Blindagem vertical: impede que um recurso use casamento de outra empresa."""

    def test_same_company_passes(self):
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        stub = WeddingOwnedStub(name="válido", company=company, wedding=wedding)
        stub.full_clean()

    def test_different_company_raises_validation_error(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_b = WeddingFactory(company=company_b)

        stub = WeddingOwnedStub(name="inválido", company=company_a, wedding=wedding_b)

        with pytest.raises(ValidationError) as exc_info:
            stub.full_clean()

        assert "wedding" in exc_info.value.message_dict
        assert "outra organização" in str(exc_info.value)

    def test_save_triggers_clean(self):
        company_a = CompanyFactory()
        company_b = CompanyFactory()
        wedding_b = WeddingFactory(company=company_b)

        stub = WeddingOwnedStub(name="inválido", company=company_a, wedding=wedding_b)

        with pytest.raises(ValidationError):
            stub.save()


@pytest.mark.django_db
class TestWeddingOwnedMixinCrossWedding:
    """Consistência horizontal: FK de um recurso deve apontar para o mesmo casamento."""

    def test_same_wedding_fk_passes(self):
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        stub1 = WeddingOwnedStub(name="A", company=company, wedding=wedding)
        stub1.save()
        stub2 = WeddingOwnedStub(name="B", company=company, wedding=wedding)
        stub2.save()

        stub1.related_item = stub2
        stub1.full_clean()

    def test_different_wedding_fk_raises_validation_error(self):
        company = CompanyFactory()
        wedding_a = WeddingFactory(company=company)
        wedding_b = WeddingFactory(company=company)

        stub1 = WeddingOwnedStub(name="A", company=company, wedding=wedding_a)
        stub1.save()
        stub2 = WeddingOwnedStub(name="B", company=company, wedding=wedding_b)
        stub2.save()

        stub1.related_item = stub2

        with pytest.raises(ValidationError) as exc_info:
            stub1.full_clean()

        assert "related_item" in exc_info.value.message_dict
        assert "outro casamento" in str(exc_info.value)


@pytest.mark.django_db
class TestWeddingOwnedMixinEdgeCases:
    def test_related_obj_none_skips_cross_wedding_check(self):
        """FK nula (related_item=None) não dispara validação horizontal."""
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        stub = WeddingOwnedStub(
            name="sem related", company=company, wedding=wedding, related_item=None
        )

        stub.full_clean()

    def test_vertical_guard_fires_before_horizontal(self):
        """Erro cross-tenant é detectado antes da validação cross-wedding."""
        company = CompanyFactory()
        company_b = CompanyFactory()
        wedding_b = WeddingFactory(company=company_b)

        stub = WeddingOwnedStub(
            name="violação vertical", company=company, wedding=wedding_b
        )

        with pytest.raises(ValidationError) as exc_info:
            stub.full_clean()

        assert "wedding" in exc_info.value.message_dict


@pytest.mark.django_db
class TestWeddingOwnedMixinPerformance:
    def test_null_fk_does_not_cause_extra_query(self):
        """FK nula não dispara query extra durante full_clean()."""
        company = CompanyFactory()
        wedding = WeddingFactory(company=company)

        stub = WeddingOwnedStub(
            name="test", company=company, wedding=wedding, related_item=None
        )

        stub.full_clean()

    def test_cross_wedding_fk_still_detected(self):
        """FK não-nula com wedding diferente ainda é detectada e rejeitada."""
        company = CompanyFactory()
        wedding_a = WeddingFactory(company=company)
        wedding_b = WeddingFactory(company=company)

        stub_a = WeddingOwnedStub(name="A", company=company, wedding=wedding_a)
        stub_a.save()
        stub_b = WeddingOwnedStub(name="B", company=company, wedding=wedding_b)
        stub_b.save()

        stub_a.related_item = stub_b

        with pytest.raises(ValidationError) as exc_info:
            stub_a.full_clean()

        assert "related_item" in exc_info.value.message_dict
