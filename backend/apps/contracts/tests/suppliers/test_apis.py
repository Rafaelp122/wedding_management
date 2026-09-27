"""Testes de API para o CRUD de Fornecedores (apps.contracts)."""

from __future__ import annotations

from typing import Any, cast

import pytest

from apps.contracts.models import Supplier
from apps.contracts.tests.factories import SupplierFactory as _SupplierFactory
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Any:
    return _WeddingFactory(*args, **kwargs)


@pytest.mark.django_db
class TestSupplierAPI:
    """CRUD de fornecedores com isolamento de tenant e validação de CNPJ."""

    def test_create_supplier_returns_201(self, auth_client: Any, user: Any) -> None:
        """POST cria fornecedor e retorna 201."""
        response = auth_client.post(
            "/api/v1/suppliers/",
            data={
                "name": "Buffet Real",
                "cnpj": "11.222.333/0001-81",
                "phone": "11999999999",
                "email": "contato@buffet.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Buffet Real"
        assert data["uuid"]

    def test_create_supplier_invalid_cnpj_returns_422(
        self, auth_client: Any, user: Any
    ) -> None:
        """CNPJ fora do formato retorna 422."""
        response = auth_client.post(
            "/api/v1/suppliers/",
            data={
                "name": "Buffet Fake",
                "cnpj": "123",
                "phone": "11999999999",
                "email": "fake@buffet.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_list_suppliers_isolation(self, auth_client: Any, user: Any) -> None:
        """Listagem retorna apenas fornecedores do tenant."""
        SupplierFactory(company=user.company, name="Fornecedor Meu")
        other = SupplierFactory(name="Fornecedor Outro")

        response = auth_client.get("/api/v1/suppliers/")
        assert response.status_code == 200
        names = [item["name"] for item in response.json()["items"]]
        assert "Fornecedor Meu" in names
        assert "Fornecedor Outro" not in names
        assert other.company_id != user.company.id

    def test_retrieve_supplier_cross_tenant_returns_404(
        self, auth_client: Any, user: Any
    ) -> None:
        """Leitura de fornecedor de outro tenant retorna 404."""
        other = SupplierFactory(name="Fornecedor Outro")

        response = auth_client.get(f"/api/v1/suppliers/{other.uuid}/")
        assert response.status_code == 404

    def test_update_and_delete_supplier(self, auth_client: Any, user: Any) -> None:
        """PATCH atualiza e DELETE remove com 204."""
        supplier = SupplierFactory(company=user.company, name="Nome Antigo")

        patch = auth_client.patch(
            f"/api/v1/suppliers/{supplier.uuid}/",
            data={"name": "Nome Novo"},
            content_type="application/json",
        )
        assert patch.status_code == 200
        assert patch.json()["name"] == "Nome Novo"

        delete = auth_client.delete(f"/api/v1/suppliers/{supplier.uuid}/")
        assert delete.status_code == 204
