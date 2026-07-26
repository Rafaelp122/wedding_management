"""
Testes CRÍTICOS para BaseModel - Validação automática no save() e conformidade ADR-011.

Garantir que o full_clean() é chamado automaticamente no save() por padrão,
que exceções são lançadas ao violar constraints e validadores, e que
skip_clean=True permite ignorar validações de código mantendo integridade no DB.
"""

import uuid
from typing import Any, cast

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, models
from django.utils import timezone

from apps.core.models import BaseModel


class BaseModelStub(BaseModel):
    """Modelo de teste para validar BaseModel."""

    objects: models.Manager[Any] = models.Manager()

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        app_label = "core"


class BaseModelCleanStub(BaseModel):
    """Modelo de teste com validação customizada no clean()."""

    objects: models.Manager[Any] = models.Manager()

    title = models.CharField(max_length=50)
    code = models.CharField(max_length=10)

    class Meta:
        app_label = "core"

    def clean(self) -> None:
        super().clean()
        if self.title and "PROHIBITED" in self.title:
            raise ValidationError({"title": "Título proibido informado."})


@pytest.mark.django_db
class TestBaseModelValidation:
    """Testes para validação automática do BaseModel (ADR-011)."""

    def test_base_model_save_calls_full_clean_by_default(self) -> None:
        """Teste CRÍTICO ADR-011: save() chama full_clean() por padrão."""
        instance = BaseModelStub(name="Teste Válido", email="test@example.com")
        instance.save()

        assert BaseModelStub.objects.filter(email="test@example.com").exists()

    def test_base_model_save_raises_validation_error_on_invalid_data(self) -> None:
        """Teste CRÍTICO ADR-011: save() falha com dados inválidos (email)."""
        instance = BaseModelStub(name="Teste", email="email-invalido")

        with pytest.raises(ValidationError) as exc_info:
            instance.save()

        assert "email" in str(exc_info.value).lower()

    def test_base_model_save_executes_custom_clean(self) -> None:
        """Teste CRÍTICO ADR-011: save() executa método clean() customizado."""
        instance = BaseModelCleanStub(title="PROHIBITED_TITLE", code="XYZ")

        with pytest.raises(ValidationError) as exc_info:
            instance.save()

        assert "title" in exc_info.value.message_dict
        assert "Título proibido" in str(exc_info.value.message_dict["title"])

    def test_base_model_save_with_skip_clean_bypasses_validation(self) -> None:
        """Teste CRÍTICO ADR-011: skip_clean=True pula validação Python."""
        instance = BaseModelStub(name="Teste", email="email-invalido")
        instance.save(skip_clean=True)

        assert BaseModelStub.objects.filter(name="Teste").exists()

    def test_base_model_save_with_skip_clean_bypasses_custom_clean(self) -> None:
        """Teste CRÍTICO ADR-011: skip_clean=True ignora clean() customizado."""
        instance = BaseModelCleanStub(title="PROHIBITED_TITLE", code="ABC")
        instance.save(skip_clean=True)

        assert BaseModelCleanStub.objects.filter(code="ABC").exists()

    def test_base_model_db_constraints_still_enforced_when_skip_clean_true(
        self,
    ) -> None:
        """
        Teste CRÍTICO ADR-011: skip_clean=True mantém integridade no banco.
        """
        BaseModelStub(name="Primeiro", email="duplicado@example.com").save()

        segundo = BaseModelStub(name="Segundo", email="duplicado@example.com")
        with pytest.raises(IntegrityError):
            segundo.save(skip_clean=True)

    def test_base_model_get_by_uuid(self) -> None:
        """Teste CRÍTICO: Método get_by_uuid funciona corretamente com UUID obj."""
        instance = BaseModelStub(name="Teste UUID", email="uuid@example.com")
        instance.save()

        found = BaseModelStub.get_by_uuid(instance.uuid)

        assert found is not None
        assert found.id == instance.id
        assert found.uuid == instance.uuid

    def test_base_model_get_by_uuid_with_invalid_uuid(self) -> None:
        """Teste CRÍTICO: get_by_uuid retorna None para UUID não existente."""
        non_existent_uuid = uuid.uuid4()
        result = BaseModelStub.get_by_uuid(non_existent_uuid)

        assert result is None

    def test_base_model_get_by_uuid_with_string_uuid(self) -> None:
        """Teste CRÍTICO: get_by_uuid aceita string UUID."""
        instance = BaseModelStub(name="Teste String UUID", email="string@example.com")
        instance.save()

        found = BaseModelStub.get_by_uuid(str(instance.uuid))

        assert found is not None
        assert found.id == instance.id

    def test_base_model_get_by_uuid_with_invalid_uuid_string(self) -> None:
        """get_by_uuid com string inválida propaga ValidationError do Django."""
        with pytest.raises(ValidationError):
            BaseModelStub.get_by_uuid("abc")

    def test_base_model_abstract_meta(self) -> None:
        """Teste CRÍTICO: BaseModel é abstrato."""
        assert BaseModel._meta.abstract is True

    def test_base_model_has_expected_fields(self) -> None:
        """Teste CRÍTICO: BaseModel tem os campos esperados."""
        expected_fields = ["id", "uuid", "created_at", "updated_at"]

        for field_name in expected_fields:
            assert hasattr(BaseModel, field_name)

        assert isinstance(BaseModel._meta.get_field("id"), models.BigAutoField)
        assert isinstance(BaseModel._meta.get_field("uuid"), models.UUIDField)
        assert isinstance(BaseModel._meta.get_field("created_at"), models.DateTimeField)
        assert isinstance(BaseModel._meta.get_field("updated_at"), models.DateTimeField)

    def test_base_model_timestamps_auto_populated(self) -> None:
        """Teste CRÍTICO: created_at e updated_at são preenchidos automaticamente."""
        import time

        instance = BaseModelStub(name="Timestamps", email="timestamps@example.com")

        assert instance.created_at is None
        assert instance.updated_at is None

        instance.save()

        assert instance.created_at is not None
        assert instance.updated_at is not None
        assert instance.created_at <= timezone.now()
        assert instance.updated_at <= timezone.now()

        old_created_at = instance.created_at
        old_updated_at = instance.updated_at
        time.sleep(0.001)
        instance.name = "Updated"
        instance.save()

        assert instance.updated_at > old_updated_at
        assert instance.created_at == old_created_at

    def test_base_model_uuid_unique_and_indexed(self) -> None:
        """Teste CRÍTICO: UUID é único e indexado."""
        uuid_field = cast(Any, BaseModel._meta.get_field("uuid"))

        assert uuid_field.unique is True
        assert uuid_field.db_index is True
        assert hasattr(uuid_field, "default")

    def test_base_model_inheritance_works_correctly(self) -> None:
        """Teste CRÍTICO: Modelos que herdam de BaseModel funcionam."""
        assert issubclass(BaseModelStub, BaseModel)
        assert issubclass(BaseModelStub, models.Model)

        for field_name in ["id", "uuid", "created_at", "updated_at"]:
            assert hasattr(BaseModelStub, field_name)

    def test_base_model_validation_integration_with_services(self) -> None:
        """Teste CRÍTICO: Validação integra com a Service Layer."""
        instance = BaseModelStub(name="", email="test@example.com")

        with pytest.raises(ValidationError) as exc_info:
            instance.save()

        error_messages = exc_info.value.message_dict
        assert "name" in error_messages
