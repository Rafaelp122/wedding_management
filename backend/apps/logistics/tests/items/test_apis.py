import pytest

from apps.logistics.tests.factories import ItemFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.api
class TestItemAPI:
    """Testes de integração para a API de Itens - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_items_isolation(self, auth_client, user):
        """Garante que um planner só vê itens dos SEUS casamentos."""
        my_wedding = WeddingFactory(planner=user)
        ItemFactory(wedding=my_wedding, name="Meu Item")

        # Item de outro planner
        ItemFactory(name="Item Alheio")

        response = auth_client.get("/api/v1/logistics/items/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Meu Item"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_item_forbidden(self, auth_client):
        """Segurança: Não pode acessar item de outro planner."""
        other_item = ItemFactory()
        response = auth_client.get(f"/api/v1/logistics/items/{other_item.uuid}/")
        assert response.status_code == 404

    def test_create_item_success(self, auth_client, user):
        """Cenário feliz de criação."""
        wedding = WeddingFactory(planner=user)
        payload = {"wedding": str(wedding.uuid), "name": "Mesa Redonda", "quantity": 10}
        response = auth_client.post(
            "/api/v1/logistics/items/", data=payload, content_type="application/json"
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Mesa Redonda"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_item_isolation(self, auth_client):
        """Segurança: Não pode atualizar item de outro planner."""
        other_item = ItemFactory(name="Original")
        response = auth_client.patch(
            f"/api/v1/logistics/items/{other_item.uuid}/",
            data={"name": "Hackeado"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_item_isolation(self, auth_client):
        """Segurança: Não pode deletar item de outro planner."""
        other_item = ItemFactory()
        response = auth_client.delete(f"/api/v1/logistics/items/{other_item.uuid}/")
        assert response.status_code == 404
