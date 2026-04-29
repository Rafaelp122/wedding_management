import pytest

from apps.logistics.tests.factories import SupplierFactory


@pytest.mark.django_db
@pytest.mark.api
class TestSupplierAPI:
    """
    Testes de integração para a API de Fornecedores - Conforme TESTING_STANDARDS.md.
    """

    @pytest.mark.multitenancy
    def test_list_suppliers_isolation(self, auth_client, user):
        """Garante que um planner só vê seus próprios fornecedores."""
        SupplierFactory(company=user.company, name="Meu Fornecedor")
        SupplierFactory(name="Outro")  # Company aleatória

        response = auth_client.get("/api/v1/logistics/suppliers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Meu Fornecedor"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_supplier_forbidden(self, auth_client):
        """Segurança: Não pode ler detalhes de fornecedor alheio."""
        other_supplier = SupplierFactory(name="Secreto")
        response = auth_client.get(
            f"/api/v1/logistics/suppliers/{other_supplier.uuid}/"
        )
        assert response.status_code == 404

    def test_create_supplier_success(self, auth_client, user):
        """Cenário feliz de criação."""
        payload = {
            "name": "Nova Empresa",
            "email": "contato@nova.com",
            "cnpj": "12.345.678/0001-90",
            "phone": "(11) 99999-8888",
        }
        response = auth_client.post(
            "/api/v1/logistics/suppliers/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Nova Empresa"

    def test_update_supplier_success(self, auth_client, user):
        """Cenário feliz de atualização."""
        supplier = SupplierFactory(company=user.company, name="Antigo")
        response = auth_client.patch(
            f"/api/v1/logistics/suppliers/{supplier.uuid}/",
            data={"name": "Novo Nome"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Novo Nome"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_supplier_isolation(self, auth_client):
        """Segurança: Não pode atualizar fornecedor de outro planner."""
        other_supplier = SupplierFactory(name="Intocável")
        response = auth_client.patch(
            f"/api/v1/logistics/suppliers/{other_supplier.uuid}/",
            data={"name": "Hackeado"},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_delete_supplier_success(self, auth_client, user):
        """Cenário feliz de deleção."""
        supplier = SupplierFactory(company=user.company)
        response = auth_client.delete(f"/api/v1/logistics/suppliers/{supplier.uuid}/")
        assert response.status_code == 204

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_supplier_isolation(self, auth_client):
        """Segurança: Não pode deletar fornecedor de outro planner."""
        other_supplier = SupplierFactory()
        response = auth_client.delete(
            f"/api/v1/logistics/suppliers/{other_supplier.uuid}/"
        )
        assert response.status_code == 404
