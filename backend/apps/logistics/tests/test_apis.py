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
        user.company,
        {
            "bride_name": "Minha",
            "groom_name": "Noz",
            "location": "Local",
            "date": "2026-10-10",
        },
    )
    my_supplier = SupplierService.create(
        user.company,
        {"name": "Fornecedor Meu", "cnpj": "0", "phone": "0", "email": "a@email.com"},
    )
    my_contract = ContractService.create(
        user.company,
        {
            "wedding": my_wedding,
            "supplier": my_supplier,
            "name": "Contrato Teste",
            "total_amount": "100.00",
            "status": "DRAFT",
        },
    )
    BudgetService.get_or_create_for_wedding(user.company, my_wedding.uuid)
    my_item = ItemService.create(
        user.company,
        {
            "wedding": my_wedding.uuid,
            "contract": my_contract.uuid,
            "name": "Item Meu",
            "quantity": 1,
        },
    )

    # Planner alheio
    from apps.users.tests.factories import UserFactory

    other_user = UserFactory(email="a@a.com")
    other_user.set_password("123")
    other_user.save()
    other_wedding = WeddingService.create(
        other_user.company,
        {
            "bride_name": "Outra",
            "groom_name": "Noz",
            "location": "Local",
            "date": "2026-10-10",
        },
    )
    other_supplier = SupplierService.create(
        other_user.company,
        {"name": "Outro", "cnpj": "1", "phone": "1", "email": "b@email.com"},
    )
    other_contract = ContractService.create(
        other_user.company,
        {
            "wedding": other_wedding,
            "supplier": other_supplier,
            "name": "Contrato Teste 2",
            "total_amount": "100.00",
            "status": "DRAFT",
        },
    )
    ItemService.create(
        other_user.company,
        {
            "wedding": other_wedding.uuid,
            "contract": other_contract.uuid,
            "name": "Item Outro",
            "quantity": 1,
        },
    )
    ItemService.create(
        other_user.company,
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
            "address": "Rua da Música, 456",
            "city": "Rio de Janeiro",
            "state": "RJ",
            "website": "https://bandaninja.com.br",
            "notes": "Banda de casamento",
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
        assert data["address"] == "Rua da Música, 456"
        assert data["city"] == "Rio de Janeiro"
        assert data["state"] == "RJ"
        assert data["website"] == "https://bandaninja.com.br"
        assert data["notes"] == "Banda de casamento"

    def test_list_suppliers_filter_by_search(self, auth_client, user):
        SupplierService.create(
            user.company,
            {
                "name": "Buffet Estrela",
                "cnpj": "1",
                "phone": "1",
                "email": "buffet@email.com",
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "Fotógrafo Sol",
                "cnpj": "2",
                "phone": "2",
                "email": "foto@email.com",
            },
        )
        SupplierService.create(
            user.company,
            {"name": "Outro", "cnpj": "3", "phone": "3", "email": "outro@email.com"},
        )

        response = auth_client.get("/api/v1/logistics/suppliers/?search=estrela")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Buffet Estrela"

    def test_list_suppliers_filter_by_is_active(self, auth_client, user):
        SupplierService.create(
            user.company,
            {
                "name": "Ativo",
                "cnpj": "1",
                "phone": "1",
                "email": "a@email.com",
                "is_active": True,
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "Inativo",
                "cnpj": "2",
                "phone": "2",
                "email": "b@email.com",
                "is_active": False,
            },
        )

        response = auth_client.get("/api/v1/logistics/suppliers/?is_active=false")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["name"] == "Inativo"

    def test_list_suppliers_filter_by_search_and_status(self, auth_client, user):
        SupplierService.create(
            user.company,
            {
                "name": "A Buffet",
                "cnpj": "1",
                "phone": "1",
                "email": "a@email.com",
                "is_active": True,
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "B Buffet",
                "cnpj": "2",
                "phone": "2",
                "email": "b@email.com",
                "is_active": False,
            },
        )

        response = auth_client.get(
            "/api/v1/logistics/suppliers/?search=buffet&is_active=true"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["name"] == "A Buffet"
