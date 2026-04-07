import pytest

from apps.finances.services.budget_service import BudgetService
from apps.logistics.services.contract_service import ContractService
from apps.logistics.services.item_service import ItemService
from apps.logistics.services.supplier_service import SupplierService
from apps.weddings.services import WeddingService


@pytest.fixture
def seed_data(user, django_user_model):
    # Planner alvo
    my_wedding = WeddingService.create(
        user,
        {
            "bride_name": "Minha",
            "groom_name": "Noz",
            "location": "Local",
            "date": "2026-10-10",
        },
    )
    my_supplier = SupplierService.create(
        user,
        {"name": "Fornecedor Meu", "cnpj": "0", "phone": "0", "email": "a@email.com"},
    )
    my_contract = ContractService.create(
        user,
        {
            "wedding": my_wedding,
            "supplier": my_supplier,
            "total_amount": "100.00",
            "status": "DRAFT",
        },
    )
    my_budget = BudgetService.get_or_create_for_wedding(user, my_wedding.uuid)
    cat_meu = my_budget.categories.first()
    # Contract created with my_contract.uuid - update it with budget_category
    ContractService.update(user, my_contract, {"budget_category": cat_meu})
    my_item = ItemService.create(
        user,
        {
            "wedding": my_wedding.uuid,
            "contract": my_contract.uuid,
            "name": "Item Meu",
            "quantity": 1,
        },
    )

    # Planner alheio
    other_user = django_user_model.objects.create_user(email="a@a.com", password="123")
    other_wedding = WeddingService.create(
        other_user,
        {
            "bride_name": "Outra",
            "groom_name": "Outro",
            "location": "Outro",
            "date": "2026-10-10",
        },
    )
    other_supplier = SupplierService.create(
        other_user,
        {
            "name": "Fornecedor Alheio",
            "cnpj": "1",
            "phone": "1",
            "email": "b@email.com",
        },
    )
    other_contract = ContractService.create(
        other_user,
        {
            "wedding": other_wedding,
            "supplier": other_supplier,
            "total_amount": "200.00",
            "status": "DRAFT",
        },
    )
    other_budget = BudgetService.get_or_create_for_wedding(
        other_user, other_wedding.uuid
    )
    cat_outro = other_budget.categories.first()
    ContractService.update(other_user, other_contract, {"budget_category": cat_outro})
    ItemService.create(
        other_user,
        {
            "wedding": other_wedding.uuid,
            "contract": other_contract.uuid,
            "name": "Item Alheio",
            "quantity": 1,
        },
    )

    return {
        "my_supplier": my_supplier,
        "my_contract": my_contract,
        "my_item": my_item,
    }


@pytest.mark.django_db
class TestLogisticsNinjaAPI:
    def test_list_suppliers_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/logistics/suppliers/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Fornecedor Meu"

    def test_list_contracts_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/logistics/contracts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["status"] == "DRAFT"

    def test_list_items_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/logistics/items/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Item Meu"

    def test_create_supplier_success(self, auth_client):
        payload = {
            "name": "Banda Ninja",
            "cnpj": "99.999.999/0001-99",
            "phone": "11999999999",
            "email": "banda@ninja.com",
            "is_active": True,
        }
        response = auth_client.post(
            "/api/v1/logistics/suppliers/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Banda Ninja"
        assert "uuid" in data
