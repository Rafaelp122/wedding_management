from typing import Any, cast

import pytest
from pydantic import ValidationError

from apps.core.exceptions import ObjectNotFoundError
from apps.logistics.models import Contract, Supplier
from apps.logistics.schemas import SupplierIn, SupplierPatchIn
from apps.logistics.services.supplier_service import SupplierService
from apps.logistics.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.logistics.tests.factories import (
    SupplierFactory as _SupplierFactory,
)
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


@pytest.mark.django_db
class TestSupplierServiceCreate:
    """Testes de criação de fornecedores via SupplierService."""

    def test_create_supplier_success(self, user: Any) -> None:
        """Criação de fornecedor vinculado à empresa do planner."""
        data: dict[str, Any] = {
            "name": "Buffet Master",
            "cnpj": "00.000.000/0001-00",
            "phone": "11999999999",
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
        """CNPJ com formato inválido deve disparar ValidationError."""
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
        supplier = SupplierFactory(company=user.company, name="Nome Antigo")

        updated = SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(name="Nome Novo"),
        )

        assert updated.name == "Nome Novo"

    def test_update_supplier_cross_tenant(self, user: Any) -> None:
        """Fornecedor de outro tenant não pode ser atualizado."""
        other_user = UserFactory()
        other_supplier = SupplierFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            SupplierService.update(
                user.company,
                other_supplier,
                SupplierPatchIn.model_construct(name="Hack"),
            )

    def test_update_supplier_toggle_active(self, user: Any) -> None:
        """Desativar/ativar fornecedor via is_active."""
        supplier = SupplierFactory(company=user.company, is_active=True)

        updated = SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(is_active=False),
        )

        assert updated.is_active is False

    def test_update_supplier_new_fields(self, user: Any) -> None:
        """Atualização dos campos address, city, state, website, notes."""
        supplier = SupplierFactory(company=user.company)

        updated = SupplierService.update(
            user.company,
            supplier,
            SupplierPatchIn.model_construct(
                address="Av. Paulista, 1000",
                city="São Paulo",
                state="SP",
                website="https://example.com",
                notes="Observação atualizada",
            ),
        )

        assert updated.address == "Av. Paulista, 1000"
        assert updated.city == "São Paulo"
        assert updated.state == "SP"
        assert updated.website == "https://example.com"
        assert updated.notes == "Observação atualizada"


@pytest.mark.django_db
class TestSupplierServiceDelete:
    """Testes de deleção de fornecedores via SupplierService."""

    def test_delete_supplier_success(self, user: Any) -> None:
        """Deleção de fornecedor sem contratos é permitida."""
        supplier = SupplierFactory(company=user.company)

        SupplierService.delete(user.company, supplier)

        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0

    def test_delete_supplier_cascades_to_contracts(self, user: Any) -> None:
        """Fornecedor com contratos: CASCADE deleta contratos junto.
        (Contract.supplier é on_delete=CASCADE, sem proteção de integridade via FK.)"""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        SupplierService.delete(user.company, supplier)

        # Ambos foram deletados (CASCADE)
        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0
        assert Contract.objects.filter(uuid=contract.uuid).count() == 0

    def test_delete_supplier_cross_tenant(self, user: Any) -> None:
        """Fornecedor de outro tenant não pode ser deletado."""
        other_user = UserFactory()
        other_supplier = SupplierFactory(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            SupplierService.delete(user.company, instance=other_supplier)
