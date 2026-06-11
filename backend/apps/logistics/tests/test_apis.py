import pytest
from django.core.files.uploadedfile import SimpleUploadedFile

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
        {"name": "Fornecedor Meu", "cnpj": "", "phone": "0", "email": "a@email.com"},
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
        {"name": "Outro", "cnpj": "", "phone": "1", "email": "b@email.com"},
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

    def test_create_supplier_invalid_cnpj_returns_422(self, auth_client):
        payload = {
            "name": "CNPJ Inválido",
            "cnpj": "123",
            "phone": "11999999999",
            "email": "invalido@email.com",
        }
        response = auth_client.post(
            "/api/v1/logistics/suppliers/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_supplier_invalid_cnpj_shows_friendly_message(self, auth_client):
        """CNPJ inválido deve retornar 422 com mensagem amigável, não regex cru."""
        payload = {
            "name": "CNPJ Inválido",
            "cnpj": "00.000.000/0000-0X",  # tamanho correto, formato inválido
            "phone": "11999999999",
            "email": "invalido@email.com",
        }
        response = auth_client.post(
            "/api/v1/logistics/suppliers/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 422
        body = response.json()
        detail = str(body.get("detail", ""))
        assert "formato" in detail.lower() or "XX.XXX" in detail

    def test_list_suppliers_filter_by_search(self, auth_client, user):
        SupplierService.create(
            user.company,
            {
                "name": "Buffet Estrela",
                "cnpj": "",
                "phone": "1",
                "email": "buffet@email.com",
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "Fotógrafo Sol",
                "cnpj": "",
                "phone": "2",
                "email": "foto@email.com",
            },
        )
        SupplierService.create(
            user.company,
            {"name": "Outro", "cnpj": "", "phone": "3", "email": "outro@email.com"},
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
                "cnpj": "",
                "phone": "1",
                "email": "a@email.com",
                "is_active": True,
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "Inativo",
                "cnpj": "",
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
                "cnpj": "",
                "phone": "1",
                "email": "a@email.com",
                "is_active": True,
            },
        )
        SupplierService.create(
            user.company,
            {
                "name": "B Buffet",
                "cnpj": "",
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

    def test_update_contract_success(self, auth_client, seed_data):
        """Testa atualização de contrato com PATCH."""
        contract = seed_data["my_contract"]
        payload = {"name": "Contrato Atualizado"}
        response = auth_client.patch(
            f"/api/v1/logistics/contracts/{contract.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Contrato Atualizado"

    def test_delete_contract_success(self, auth_client, seed_data):
        """Testa exclusão de contrato com DELETE."""
        contract = seed_data["my_contract"]
        response = auth_client.delete(f"/api/v1/logistics/contracts/{contract.uuid}/")
        assert response.status_code == 204

    def test_update_item_success(self, auth_client, seed_data):
        """Testa atualização de item com PATCH."""
        item = seed_data["my_item"]
        payload = {"name": "Item Atualizado"}
        response = auth_client.patch(
            f"/api/v1/logistics/items/{item.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Item Atualizado"

    def test_delete_item_success(self, auth_client, seed_data):
        """Testa exclusão de item com DELETE."""
        item = seed_data["my_item"]
        response = auth_client.delete(f"/api/v1/logistics/items/{item.uuid}/")
        assert response.status_code == 204

    def test_update_supplier_success(self, auth_client, seed_data):
        """Testa atualização de fornecedor com PATCH."""
        supplier = seed_data["my_supplier"]
        payload = {"name": "Fornecedor Atualizado"}
        response = auth_client.patch(
            f"/api/v1/logistics/suppliers/{supplier.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Fornecedor Atualizado"

    def test_delete_supplier_success(self, auth_client, seed_data):
        """Testa exclusão de fornecedor com DELETE."""
        supplier = seed_data["my_supplier"]
        response = auth_client.delete(f"/api/v1/logistics/suppliers/{supplier.uuid}/")
        assert response.status_code == 204

    def test_retrieve_contract(self, auth_client, seed_data):
        response = auth_client.get(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/"
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Contrato Teste"

    def test_create_contract_via_api(self, auth_client, seed_data):
        payload = {
            "wedding": str(seed_data["my_contract"].wedding.uuid),
            "supplier": str(seed_data["my_supplier"].uuid),
            "name": "Contrato API",
            "total_amount": "500.00",
            "status": "DRAFT",
        }
        response = auth_client.post(
            "/api/v1/logistics/contracts/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Contrato API"

    def test_upload_contract_file(self, auth_client, seed_data):
        pdf = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        response = auth_client.post(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/upload/",
            data={"pdf_file": pdf},
        )
        assert response.status_code == 200

    def test_delete_contract_file(self, auth_client, seed_data):
        pdf = SimpleUploadedFile("test.pdf", b"content", content_type="application/pdf")
        auth_client.post(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/upload/",
            data={"pdf_file": pdf},
        )
        response = auth_client.delete(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/upload/",
        )
        assert response.status_code == 204

    def test_transition_contract_status(self, auth_client, seed_data):
        """DRAFT → PENDING (transição válida)."""
        response = auth_client.post(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}"
            f"/transition-status/",
            data={"status": "PENDING"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PENDING"

    def test_retrieve_item(self, auth_client, seed_data):
        response = auth_client.get(
            f"/api/v1/logistics/items/{seed_data['my_item'].uuid}/"
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Item Meu"

    def test_create_item_via_api(self, auth_client, seed_data):
        payload = {
            "wedding": str(seed_data["my_contract"].wedding.uuid),
            "contract": str(seed_data["my_contract"].uuid),
            "name": "Item API",
            "quantity": 3,
        }
        response = auth_client.post(
            "/api/v1/logistics/items/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Item API"

    def test_transition_item_status(self, auth_client, seed_data):
        """PENDING → IN_PROGRESS → DONE."""
        # Primeiro PENDING → IN_PROGRESS
        auth_client.post(
            f"/api/v1/logistics/items/{seed_data['my_item'].uuid}/transition-status/",
            data={"acquisition_status": "IN_PROGRESS"},
            content_type="application/json",
        )
        # Depois IN_PROGRESS → DONE
        response = auth_client.post(
            f"/api/v1/logistics/items/{seed_data['my_item'].uuid}/transition-status/",
            data={"acquisition_status": "DONE"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["acquisition_status"] == "DONE"

    def test_retrieve_supplier(self, auth_client, seed_data):
        response = auth_client.get(
            f"/api/v1/logistics/suppliers/{seed_data['my_supplier'].uuid}/"
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Fornecedor Meu"


@pytest.mark.django_db
class TestLogisticsAPIAuth:
    def test_contracts_requires_auth(self, client):
        """Verifica que listar contratos sem autenticação retorna 401."""
        response = client.get("/api/v1/logistics/contracts/")
        assert response.status_code == 401

    def test_items_requires_auth(self, client):
        """Verifica que listar itens sem autenticação retorna 401."""
        response = client.get("/api/v1/logistics/items/")
        assert response.status_code == 401

    def test_suppliers_requires_auth(self, client):
        """Verifica que listar fornecedores sem autenticação retorna 401."""
        response = client.get("/api/v1/logistics/suppliers/")
        assert response.status_code == 401
