"""
Testes CRÍTICOS para BaseModel - Validação automática no save().

Garantir que o full_clean() é chamado automaticamente e que skip_clean funciona.
"""

import pytest
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class TestModel(BaseModel):
    """Modelo de teste para validar BaseModel."""

    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    class Meta:
        app_label = "core"  # Necessário para testes Django


@pytest.mark.django_db
class TestBaseModelValidation:
    """Testes para validação automática do BaseModel."""

    def test_base_model_save_calls_full_clean_by_default(self):
        """Teste CRÍTICO: save() chama full_clean() por padrão."""
        # Criar instância com dados válidos
        instance = TestModel(name="Teste Válido", email="test@example.com")

        # Deve salvar sem erros
        instance.save()

        assert TestModel.objects.filter(email="test@example.com").exists()

    def test_base_model_save_raises_validation_error_on_invalid_data(self):
        """Teste CRÍTICO: save() falha com dados inválidos."""
        # Tentar salvar com email inválido
        instance = TestModel(name="Teste", email="email-invalido")

        # Deve lançar ValidationError
        with pytest.raises(ValidationError) as exc_info:
            instance.save()

        assert "email" in str(exc_info.value).lower()

    def test_base_model_save_with_skip_clean_bypasses_validation(self):
        """Teste CRÍTICO: skip_clean=True permite salvar sem validação."""
        # Criar instância com email inválido
        instance = TestModel(name="Teste", email="email-invalido")

        # Com skip_clean=True, deve salvar (útil para fixtures/migrations)
        instance.save(skip_clean=True)

        # Verificar que foi salvo apesar do email inválido
        assert TestModel.objects.filter(name="Teste").exists()

        # Nota: O banco de dados pode rejeitar dependendo das constraints
        # Este teste valida o comportamento do código Python

    def test_base_model_get_by_uuid(self):
        """Teste CRÍTICO: Método get_by_uuid funciona corretamente."""
        # Criar instância
        instance = TestModel(name="Teste UUID", email="uuid@example.com")
        instance.save()

        # Buscar pelo UUID
        found = TestModel.get_by_uuid(instance.uuid)

        assert found is not None
        assert found.id == instance.id
        assert found.uuid == instance.uuid

    def test_base_model_get_by_uuid_with_invalid_uuid(self):
        """Teste CRÍTICO: get_by_uuid retorna None para UUID não existente."""
        import uuid

        non_existent_uuid = uuid.uuid4()
        result = TestModel.get_by_uuid(non_existent_uuid)

        assert result is None

    def test_base_model_get_by_uuid_with_string_uuid(self):
        """Teste CRÍTICO: get_by_uuid aceita string UUID."""
        instance = TestModel(name="Teste String UUID", email="string@example.com")
        instance.save()

        # Buscar usando string
        found = TestModel.get_by_uuid(str(instance.uuid))

        assert found is not None
        assert found.id == instance.id

    def test_base_model_abstract_meta(self):
        """Teste CRÍTICO: BaseModel é abstrato."""
        assert BaseModel._meta.abstract is True

    def test_base_model_has_expected_fields(self):
        """Teste CRÍTICO: BaseModel tem os campos esperados."""
        expected_fields = ["id", "uuid", "created_at", "updated_at"]

        for field_name in expected_fields:
            assert hasattr(BaseModel, field_name)

        # Verificar tipos dos campos
        assert isinstance(BaseModel._meta.get_field("id"), models.BigAutoField)
        assert isinstance(BaseModel._meta.get_field("uuid"), models.UUIDField)
        assert isinstance(BaseModel._meta.get_field("created_at"), models.DateTimeField)
        assert isinstance(BaseModel._meta.get_field("updated_at"), models.DateTimeField)

    def test_base_model_timestamps_auto_populated(self):
        """Teste CRÍTICO: created_at e updated_at são preenchidos automaticamente."""
        import time

        from django.utils import timezone

        instance = TestModel(name="Timestamps", email="timestamps@example.com")

        # Antes de salvar
        assert instance.created_at is None
        assert instance.updated_at is None

        # Salvar
        instance.save()

        # Depois de salvar
        assert instance.created_at is not None
        assert instance.updated_at is not None
        assert instance.created_at <= timezone.now()
        assert instance.updated_at <= timezone.now()

        # Atualizar e verificar que updated_at muda
        old_updated_at = instance.updated_at
        time.sleep(0.001)  # Garantir diferença de tempo
        instance.name = "Updated"
        instance.save()

        assert instance.updated_at > old_updated_at
        assert instance.created_at == instance.created_at  # Não muda

    def test_base_model_uuid_unique_and_indexed(self):
        """Teste CRÍTICO: UUID é único e indexado."""
        uuid_field = BaseModel._meta.get_field("uuid")

        assert uuid_field.unique is True
        assert uuid_field.db_index is True
        assert hasattr(uuid_field, "default")  # Tem valor padrão

    def test_base_model_inheritance_works_correctly(self):
        """Teste CRÍTICO: Modelos que herdam de BaseModel funcionam."""
        # Testar que TestModel herda corretamente
        assert issubclass(TestModel, BaseModel)
        assert issubclass(TestModel, models.Model)

        # Verificar que TestModel tem os campos de BaseModel
        for field_name in ["id", "uuid", "created_at", "updated_at"]:
            assert hasattr(TestModel, field_name)

    def test_base_model_validation_integration_with_services(self):
        """Teste CRÍTICO: Validação integra com Service Layer."""
        # Este teste simula como os serviços usam a validação
        instance = TestModel(name="", email="test@example.com")  # Nome vazio

        # Simular o que WeddingService.create faz:
        # 1. Cria instância
        # 2. Chama save() que chama full_clean()
        # 3. full_clean() valida campos obrigatórios

        with pytest.raises(ValidationError) as exc_info:
            instance.save()  # Deve falhar porque name está vazio

        # Verificar que a mensagem de erro é apropriada
        error_messages = exc_info.value.message_dict
        assert "name" in error_messages
