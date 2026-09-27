"""Testes unitários para seletores de leitura de fornecedores (apps.suppliers.selectors)."""

from typing import Any

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.suppliers.selectors import supplier_get_selector, supplier_list_selector
from apps.suppliers.tests.factories import SupplierFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSupplierSelectors:
    """Suíte de testes para os seletores de leitura do domínio de fornecedores."""

    def test_supplier_list_selector_tenant_isolation(self, user: Any) -> None:
        """Listagem retorna apenas fornecedores do tenant autenticado."""
        s1 = SupplierFactory.create(company=user.company, name="Fornecedor A")
        s2 = SupplierFactory.create(company=user.company, name="Fornecedor B")

        other_user = UserFactory.create()
        SupplierFactory.create(company=other_user.company, name="Fornecedor Outro")

        results = list(supplier_list_selector(company=user.company))
        assert len(results) == 2
        assert s1 in results
        assert s2 in results

    def test_supplier_list_selector_search_filter(self, user: Any) -> None:
        """Busca textual filtra por nome, email, telefone ou CNPJ."""
        SupplierFactory.create(
            company=user.company,
            name="Buffet Sol",
            email="sol@buffet.com",
            cnpj="11.222.333/0001-81",
        )
        SupplierFactory.create(
            company=user.company,
            name="Banda Lua",
            email="lua@banda.com",
            cnpj="00.000.000/0001-91",
        )

        results = list(supplier_list_selector(company=user.company, search="Sol"))
        assert len(results) == 1
        assert results[0].name == "Buffet Sol"

        results_cnpj = list(
            supplier_list_selector(company=user.company, search="0001-91")
        )
        assert len(results_cnpj) == 1
        assert results_cnpj[0].name == "Banda Lua"

    def test_supplier_list_selector_active_filter(self, user: Any) -> None:
        """Filtro de is_active retorna apenas fornecedores com o status desejado."""
        SupplierFactory.create(company=user.company, name="Ativo", is_active=True)
        SupplierFactory.create(company=user.company, name="Inativo", is_active=False)

        actives = list(supplier_list_selector(company=user.company, is_active=True))
        assert len(actives) == 1
        assert actives[0].name == "Ativo"

        inactives = list(supplier_list_selector(company=user.company, is_active=False))
        assert len(inactives) == 1
        assert inactives[0].name == "Inativo"

    def test_supplier_get_selector_success(self, user: Any) -> None:
        """Recupera fornecedor por UUID com isolamento de tenant."""
        supplier = SupplierFactory.create(company=user.company)
        retrieved = supplier_get_selector(company=user.company, uuid=supplier.uuid)
        assert retrieved.id == supplier.id

    def test_supplier_get_selector_cross_tenant_raises_404(self, user: Any) -> None:
        """Tentativa de recuperar fornecedor de outro tenant levanta ObjectNotFoundError."""
        other_user = UserFactory.create()
        other_supplier = SupplierFactory.create(company=other_user.company)

        with pytest.raises(ObjectNotFoundError):
            supplier_get_selector(company=user.company, uuid=other_supplier.uuid)
