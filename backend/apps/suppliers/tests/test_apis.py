"""Testes de rotas da API Ninja para Fornecedores (/suppliers/)."""

from __future__ import annotations

from typing import Any

import pytest
from django.test import Client

from apps.suppliers.tests.factories import SupplierFactory
from apps.users.tests.factories import UserFactory


@pytest.mark.django_db
class TestSuppliersAPI:
    """Suíte de testes de integração dos endpoints HTTP de fornecedores."""

    def test_create_supplier_success_returns_201(
        self, auth_client: Client, user: Any
    ) -> None:
        """POST /api/v1/suppliers/ cria fornecedor com CNPJ válido e retorna 201."""
        response = auth_client.post(
            "/api/v1/suppliers/",
            data={
                "name": "Buffet Real",
                "cnpj": "11.222.333/0001-81",
                "phone": "(11) 99999-9999",
                "email": "contato@buffet.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Buffet Real"
        assert data["cnpj"] == "11.222.333/0001-81"
        assert data["uuid"]

    def test_create_supplier_invalid_cnpj_returns_422(
        self, auth_client: Client, user: Any
    ) -> None:
        """POST /api/v1/suppliers/ com CNPJ inválido retorna 422 Unprocessable Entity."""
        response = auth_client.post(
            "/api/v1/suppliers/",
            data={
                "name": "Buffet Fake",
                "cnpj": "123",
                "phone": "(11) 99999-9999",
                "email": "fake@buffet.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_supplier_invalid_modulo11_returns_422(
        self, auth_client: Client, user: Any
    ) -> None:
        """POST /api/v1/suppliers/ com CNPJ fictício 00.000.000/0001-00 retorna 422."""
        response = auth_client.post(
            "/api/v1/suppliers/",
            data={
                "name": "Buffet Fake",
                "cnpj": "00.000.000/0001-00",
                "phone": "(11) 99999-9999",
                "email": "fake@buffet.com",
            },
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_list_suppliers_tenant_isolation(
        self, auth_client: Client, user: Any
    ) -> None:
        """GET /api/v1/suppliers/ retorna apenas fornecedores do tenant logado."""
        SupplierFactory.create(company=user.company, name="Fornecedor Meu")
        other_user = UserFactory.create()
        SupplierFactory.create(company=other_user.company, name="Fornecedor Outro")

        response = auth_client.get("/api/v1/suppliers/")
        assert response.status_code == 200
        names = [item["name"] for item in response.json()["items"]]
        assert "Fornecedor Meu" in names
        assert "Fornecedor Outro" not in names

    def test_retrieve_supplier_cross_tenant_returns_404(
        self, auth_client: Client, user: Any
    ) -> None:
        """GET /api/v1/suppliers/{uuid}/ de outro tenant retorna 404."""
        other_user = UserFactory.create()
        other = SupplierFactory.create(
            company=other_user.company, name="Fornecedor Outro"
        )

        response = auth_client.get(f"/api/v1/suppliers/{other.uuid}/")
        assert response.status_code == 404

    def test_update_and_delete_supplier(self, auth_client: Client, user: Any) -> None:
        """PATCH atualiza dados e DELETE remove o cadastro com 204."""
        supplier = SupplierFactory.create(company=user.company, name="Nome Antigo")

        patch_res = auth_client.patch(
            f"/api/v1/suppliers/{supplier.uuid}/",
            data={"name": "Nome Novo"},
            content_type="application/json",
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["name"] == "Nome Novo"

        delete_res = auth_client.delete(f"/api/v1/suppliers/{supplier.uuid}/")
        assert delete_res.status_code == 204
