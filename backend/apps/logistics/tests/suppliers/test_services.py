import pytest

from apps.core.exceptions import DomainIntegrityError
from apps.logistics.models import Supplier
from apps.logistics.services.supplier_service import SupplierService
from apps.logistics.tests.factories import ContractFactory, SupplierFactory


@pytest.mark.django_db
@pytest.mark.service
class TestSupplierService:
    """
    Testes de lógica de negócio para SupplierService - Conforme TESTING_STANDARDS.md.
    """

    def test_list_suppliers_isolation(self, user):
        """Domínio: Garante filtragem por planner na listagem."""
        SupplierFactory(company=user.company)
        SupplierFactory()

        qs = SupplierService.list(user=user)
        assert qs.count() == 1

    def test_create_supplier_success(self, user):
        """Domínio: Criação de fornecedor vinculado ao planner."""
        data = {"name": "Fornecedor Teste", "email": "test@example.com"}
        supplier = SupplierService.create(user=user, data=data)

        assert supplier.company == user.company
        assert supplier.name == "Fornecedor Teste"

    def test_update_supplier_success(self, user):
        """Domínio: Atualização de campos simples."""
        supplier = SupplierFactory(company=user.company, name="Antigo")
        SupplierService.update(instance=supplier, data={"name": "Novo"})
        assert supplier.name == "Novo"

    def test_delete_supplier_success(self, user):
        """Domínio: Deleção física do registro."""
        supplier = SupplierFactory(company=user.company)
        SupplierService.delete(instance=supplier)
        assert Supplier.objects.filter(uuid=supplier.uuid).count() == 0

    def test_delete_supplier_protected_by_contract(self, user):
        """Domínio: Regra de proteção contra deleção se houver contratos."""
        supplier = SupplierFactory(company=user.company)
        ContractFactory(supplier=supplier)

        with pytest.raises(DomainIntegrityError):
            SupplierService.delete(instance=supplier)
