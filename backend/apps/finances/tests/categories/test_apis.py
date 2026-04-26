import pytest


@pytest.mark.django_db
@pytest.mark.api
class TestCategoryAPI:
    """Testes de integração para a API de Categorias - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_categories_isolation(self, auth_client, finance_seed):
        """Garante que o planner só vê categorias dos seus casamentos."""
        response = auth_client.get("/api/v1/finances/categories/")
        assert response.status_code == 200
        data = response.json()
        # Temos 6 categorias criadas no finance_seed para 'user'
        assert len(data["items"]) == 6

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_category_forbidden(self, auth_client, finance_seed):
        """Segurança: Não pode acessar categoria de outro planner."""
        other_cat = finance_seed["other_expense"].category
        response = auth_client.get(f"/api/v1/finances/categories/{other_cat.uuid}/")
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_category_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode editar categoria de outro planner."""
        other_cat = finance_seed["other_expense"].category
        response = auth_client.patch(
            f"/api/v1/finances/categories/{other_cat.uuid}/",
            data={"name": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_category_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode deletar categoria de outro planner."""
        other_cat = finance_seed["other_expense"].category
        response = auth_client.delete(f"/api/v1/finances/categories/{other_cat.uuid}/")
        assert response.status_code == 404
