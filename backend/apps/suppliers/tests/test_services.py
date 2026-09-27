"""Testes unitários para a camada de serviços de fornecedores (apps.suppliers.services)."""

from typing import Any

import pytest
from pydantic import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.suppliers.models import Supplier
from apps.suppliers.schemas import SupplierIn, SupplierPatchIn
from apps.suppliers.services import SupplierService
from apps.suppliers.tests.factories import SupplierFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSupplierServiceCreate:
    """Testes de criação de fornecedores via SupplierService."""

    def test_create_supplier_success(self, user: Any) -> None:
        """Criação de fornecedor vinculado à empresa do tenant autenticado."""
        data: dict[str, Any] = {
            "name": "Buffet Master",
            "cnpj": "11.222.333/0001-81",
            "phone": "(11) 99999-9999",
            "email": "buffet@master.com",
            "address": "Rua das Flores, 123",
            "city": "São Paulo",
            "state": "SP",
            "website": "https://buffetmaster.com.br",
            "notes": "Fornecedor premium",
        }

        supplier = SupplierService.create(user.company, SupplierIn(**data))

        assert supplier.company == user.company
        assert supplier.name == "Buffet Master"
        assert supplier.is_active is True
        assert supplier.address == "Rua das Flores, 123"
        assert supplier.city == "São Paulo"
        assert supplier.state == "SP"
        assert supplier.website == "https://buffetmaster.com.br"
        assert supplier.notes == "Fornecedor premium"

    def test_create_supplier_with_invalid_cnpj_raises_validation_error(
        self, user: Any
    ) -> None:
        """CNPJ com formato ou dígitos incorretos dispara ValidationError."""
        data: dict[str, Any] = {
            "name": "Fornecedor Inválido",
            "cnpj": "123",
            "phone": "11999999999",
            "email": "invalido@email.com",
        }

        with pytest.raises(ValidationError):
            SupplierService.create(user.company, SupplierIn(**data))


@pytest.mark.django_db
class TestSupplierServiceUpdate:
    """Testes de atualização de fornecedores via SupplierService."""

    def test_update_supplier_name(self, user: Any) -> None:
        """Atualização de nome é permitida."""
        supplier = SupplierFactory.create(company=user.company, name="Nome Antigo")

        updated = SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(name="Nome Novo"),
        )

        assert updated.name == "Nome Novo"

    def test_update_supplier_cross_tenant(self, user: Any) -> None:
        """Fornecedor de outro tenant não pode ser atualizado."""
        other_user = UserFactory.create()
        other_supplier = SupplierFactory.create(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            SupplierService.update(
                user.company,
                other_supplier,
                SupplierPatchIn.model_construct(name="Hack"),
            )

    def test_update_supplier_toggle_active(self, user: Any) -> None:
        """Desativar/ativar fornecedor via is_active."""
        supplier = SupplierFactory.create(company=user.company, is_active=True)

        updated = SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(is_active=False),
        )

        assert updated.is_active is False

    def test_update_supplier_persists_with_update_fields(
        self, user: Any, mocker: Any
    ) -> None:
        """update() persiste alterações com update_fields contendo updated_at."""
        supplier = SupplierFactory.create(company=user.company, name="Nome Antigo")
        spy_save = mocker.spy(supplier, "save")

        SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(name="Nome Novo", city="Curitiba"),
        )

        assert spy_save.call_count == 1
        _, kwargs = spy_save.call_args
        assert "update_fields" in kwargs
        update_fields = set(kwargs["update_fields"])
        assert update_fields == {"name", "city", "updated_at"}


@pytest.mark.django_db
class TestSupplierServiceDelete:
    """Testes de deleção de fornecedores via SupplierService."""

    def test_delete_supplier_success(self, user: Any) -> None:
        """Deleção de fornecedor remove a entidade do banco."""
        supplier = SupplierFactory.create(company=user.company)

        SupplierService.delete(user.company, supplier)

        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0

    def test_delete_supplier_cross_tenant(self, user: Any) -> None:
        """Fornecedor de outro tenant não pode ser deletado."""
        other_user = UserFactory.create()
        other_supplier = SupplierFactory.create(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            SupplierService.delete(user.company, instance=other_supplier)
