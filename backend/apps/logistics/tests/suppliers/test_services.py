from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.logistics.models import Contract, Supplier
from apps.logistics.services.supplier_service import SupplierService
from apps.logistics.tests.factories import ContractFactory, SupplierFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestSupplierServiceCreate:
    """Testes de criação de fornecedores via SupplierService."""

    def test_create_supplier_success(self, user):
        """Criação de fornecedor vinculado à empresa do planner."""
        data = {
            "name": "Buffet Master",
            "cnpj": "00.000.000/0001-00",
            "phone": "11999999999",
            "email": "buffet@master.com",
        }

        supplier = SupplierService.create(user.company, data)

        assert supplier.company == user.company
        assert supplier.name == "Buffet Master"
        assert supplier.is_active is True


@pytest.mark.django_db
class TestSupplierServiceUpdate:
    """Testes de atualização de fornecedores via SupplierService."""

    def test_update_supplier_name(self, user):
        """Atualização de nome é permitida."""
        supplier = SupplierFactory(company=user.company, name="Nome Antigo")

        updated = SupplierService.update(user.company, supplier, {"name": "Nome Novo"})

        assert updated.name == "Nome Novo"

    def test_update_supplier_cannot_change_company(self, user):
        """Company é bloqueada no update."""
        supplier = SupplierFactory(company=user.company)
        other_user = UserFactory()

        updated = SupplierService.update(
            user.company, supplier, {"company": other_user.company}
        )

        assert updated.company == user.company

    def test_update_supplier_toggle_active(self, user):
        """Desativar/ativar fornecedor via is_active."""
        supplier = SupplierFactory(company=user.company, is_active=True)

        updated = SupplierService.update(user.company, supplier, {"is_active": False})

        assert updated.is_active is False


@pytest.mark.django_db
class TestSupplierServiceDelete:
    """Testes de deleção de fornecedores via SupplierService."""

    def test_delete_supplier_success(self, user):
        """Deleção de fornecedor sem contratos é permitida."""
        supplier = SupplierFactory(company=user.company)

        SupplierService.delete(user.company, supplier)

        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0

    def test_delete_supplier_cascades_to_contracts(self, user):
        """Fornecedor com contratos: CASCADE deleta contratos junto.
        (Contract.supplier é on_delete=CASCADE, sem proteção de integridade via FK.)"""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        SupplierService.delete(user.company, supplier)

        # Ambos foram deletados (CASCADE)
        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0
        assert Contract.objects.filter(uuid=contract.uuid).count() == 0


@pytest.mark.django_db
class TestSupplierServiceListAndGet:
    """Testes de listagem e obtenção de fornecedores."""

    def test_list_suppliers_multitenancy(self):
        """list() retorna apenas fornecedores do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()

        SupplierFactory(company=user_a.company, name="Fornecedor A")
        SupplierFactory(company=user_b.company, name="Fornecedor B")

        qs_a = SupplierService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().name == "Fornecedor A"

        qs_b = SupplierService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().name == "Fornecedor B"

    def test_get_supplier_success(self, user):
        """get() retorna fornecedor por UUID."""
        supplier = SupplierFactory(company=user.company, name="Decorações Ltda")

        result = SupplierService.get(user.company, supplier.uuid)

        assert result.uuid == supplier.uuid
        assert result.name == "Decorações Ltda"

    def test_get_supplier_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            SupplierService.get(user.company, uuid4())

    def test_get_supplier_multitenancy(self):
        """Usuário A não pode acessar fornecedor do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        supplier_b = SupplierFactory(company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            SupplierService.get(user_a.company, supplier_b.uuid)

    def test_supplier_visible_across_weddings(self, user):
        """BR-L03: mesmo fornecedor é acessível em múltiplos casamentos."""
        supplier = SupplierFactory(company=user.company)

        # Criar dois casamentos, ambos vinculam o mesmo fornecedor
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        ContractFactory(wedding=wedding1, supplier=supplier)
        ContractFactory(wedding=wedding2, supplier=supplier)

        # Fornecedor deve aparecer apenas uma vez na listagem
        qs = SupplierService.list(user.company)
        assert qs.count() == 1
        assert qs.first() == supplier
        # E ter 2 contratos associados
        assert supplier.contracts.count() == 2
