import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.mixins import PlannerOwnedMixin
from apps.core.models import BaseModel


class MockModel(BaseModel):
    """Modelo mock para testar BaseModel."""

    name = models.CharField(max_length=100)

    class Meta:
        app_label = "core"


class MockPlannerModel(BaseModel, PlannerOwnedMixin):
    """Modelo mock para testar PlannerOwnedMixin."""

    title = models.CharField(max_length=100)

    class Meta:
        app_label = "core"


@pytest.mark.django_db
@pytest.mark.unit
class TestBaseModel:
    """Testes para as funcionalidades base do BaseModel."""

    def test_save_calls_full_clean(self):
        """Garante que o save() invoca validações do Django automaticamente."""
        instance = MockModel(name="A" * 101)  # Ultrapassa limite
        with pytest.raises(ValidationError):
            instance.save()

    def test_skip_clean_bypass(self):
        """Garante que skip_clean=True ignora validações (uso em migrations/seeds)."""
        instance = MockModel(name="A" * 101)
        instance.save(skip_clean=True)  # Não deve quebrar
        assert MockModel.objects.count() == 1

    def test_uuid_lookup(self):
        """Valida o helper get_by_uuid."""
        instance = MockModel.objects.create(name="Teste")
        found = MockModel.get_by_uuid(instance.uuid)
        assert found == instance

    def test_timestamps_auto_update(self):
        """Valida se created_at e updated_at são geridos pelo banco/django."""
        instance = MockModel.objects.create(name="Teste")
        old_updated = instance.updated_at

        instance.name = "Mudou"
        instance.save()

        assert instance.updated_at > old_updated


@pytest.mark.django_db
@pytest.mark.unit
class TestPlannerOwnedMixin:
    """Testes para o mixin de posse por Planner."""

    def test_planner_owned_integrity(self, user):
        """Garante que um modelo com o mixin exige um planner."""
        instance = MockPlannerModel(title="Teste")
        # Sem planner, o full_clean (chamado no save) deve falhar
        with pytest.raises(ValidationError):
            instance.save()

    def test_planner_assignment(self, user):
        """Garante que a atribuição de planner funciona."""
        instance = MockPlannerModel(title="Teste", planner=user)
        instance.save()
        assert instance.planner == user
