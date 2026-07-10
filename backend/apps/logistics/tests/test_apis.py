import json
from datetime import date
from decimal import Decimal

import pytest

from apps.finances.services.budget_service import BudgetService
from apps.finances.tests.factories import BudgetCategoryFactory, BudgetFactory
from apps.logistics.schemas import ContractIn, ItemIn, SupplierIn
from apps.logistics.services.contract_service import ContractService
from apps.logistics.services.item_service import ItemService
from apps.logistics.services.supplier_service import SupplierService
from apps.logistics.tests.factories import SupplierFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.schemas import WeddingIn
from apps.weddings.services import WeddingService
from apps.weddings.tests.factories import WeddingFactory


@pytest.fixture
def seed_data(user, django_user_model):
    # Planner alvo
    my_wedding = WeddingService.create(
        user.company,
        WeddingIn(
            bride_name="Minha",
            groom_name="Noz",
            location="Local",
            date=date(2026, 10, 10),
        ),
    )
    my_supplier = SupplierService.create(
        user.company,
        SupplierIn(
            name="Fornecedor Meu",
            cnpj="00.000.000/0001-00",
            phone="0",
            email="a@email.com",
        ),
    )
    my_contract = ContractService.create(
        user.company,
        ContractIn(
            wedding=my_wedding.uuid,
            supplier=my_supplier.uuid,
            name="Contrato Teste",
            total_amount=Decimal("100.00"),
            status="DRAFT",
        ),
    )
    BudgetService.get_or_create_for_wedding(user.company, my_wedding.uuid)
    my_item = ItemService.create(
        user.company,
        ItemIn(
            wedding=my_wedding.uuid,
            contract=my_contract.uuid,
            name="Item Meu",
            quantity=1,
        ),
    )

    # Planner alheio
    from apps.users.tests.factories import UserFactory

    other_user = UserFactory(email="a@a.com")
    other_user.set_password("123")
    other_user.save()
    other_wedding = WeddingService.create(
        other_user.company,
        WeddingIn(
            bride_name="Outra",
            groom_name="Noz",
            location="Local",
            date=date(2026, 10, 10),
        ),
    )
    other_supplier = SupplierService.create(
        other_user.company,
        SupplierIn(
            name="Outro", cnpj="00.000.000/0001-01", phone="1", email="b@email.com"
        ),
    )
    other_contract = ContractService.create(
        other_user.company,
        ContractIn(
            wedding=other_wedding.uuid,
            supplier=other_supplier.uuid,
            name="Contrato Teste 2",
            total_amount=Decimal("100.00"),
            status="DRAFT",
        ),
    )
    ItemService.create(
        other_user.company,
        ItemIn(
            wedding=other_wedding.uuid,
            contract=other_contract.uuid,
            name="Item Outro",
            quantity=1,
        ),
    )
    ItemService.create(
        other_user.company,
        ItemIn(
            wedding=other_wedding.uuid,
            contract=other_contract.uuid,
            name="Item Alheio",
            quantity=1,
        ),
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

    def test_list_contracts_filter_by_parent(self, auth_client, seed_data):
        """GET /api/v1/logistics/contracts/?parent_id=X retorna só aditivos."""
        response = auth_client.get(
            f"/api/v1/logistics/contracts/?parent_id={seed_data['my_contract'].uuid}"
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0  # seed_data não cria aditivos

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
            SupplierIn(
                name="Buffet Estrela",
                cnpj="00.000.000/0001-00",
                phone="1",
                email="buffet@email.com",
            ),
        )
        SupplierService.create(
            user.company,
            SupplierIn(
                name="Fotógrafo Sol",
                cnpj="00.000.000/0001-00",
                phone="2",
                email="foto@email.com",
            ),
        )
        SupplierService.create(
            user.company,
            SupplierIn(
                name="Outro",
                cnpj="00.000.000/0001-00",
                phone="3",
                email="outro@email.com",
            ),
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
            SupplierIn(
                name="Ativo",
                cnpj="00.000.000/0001-00",
                phone="1",
                email="a@email.com",
                is_active=True,
            ),
        )
        SupplierService.create(
            user.company,
            SupplierIn(
                name="Inativo",
                cnpj="00.000.000/0001-00",
                phone="2",
                email="b@email.com",
                is_active=False,
            ),
        )

        response = auth_client.get("/api/v1/logistics/suppliers/?is_active=false")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 1
        assert data["items"][0]["name"] == "Inativo"

    def test_list_suppliers_filter_by_search_and_status(self, auth_client, user):
        SupplierService.create(
            user.company,
            SupplierIn(
                name="A Buffet",
                cnpj="00.000.000/0001-00",
                phone="1",
                email="a@email.com",
                is_active=True,
            ),
        )
        SupplierService.create(
            user.company,
            SupplierIn(
                name="B Buffet",
                cnpj="00.000.000/0001-00",
                phone="2",
                email="b@email.com",
                is_active=False,
            ),
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

    def test_update_contract_wedding_field_is_ignored(
        self, auth_client, seed_data, user
    ):
        """
        Testa que enviar o campo wedding no PATCH do contrato é ignorado (200)
        e não altera o casamento.
        """
        contract = seed_data["my_contract"]
        other_wedding = WeddingFactory(company=user.company)
        payload = {"name": "Novo Nome", "wedding": str(other_wedding.uuid)}
        response = auth_client.patch(
            f"/api/v1/logistics/contracts/{contract.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        contract.refresh_from_db()
        assert contract.name == "Novo Nome"
        assert contract.wedding.uuid == seed_data["my_contract"].wedding.uuid

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

    def test_update_item_wedding_field_is_ignored(self, auth_client, seed_data, user):
        """
        Testa que enviar o campo wedding no PATCH do item é ignorado (200)
        e não altera o casamento.
        """
        item = seed_data["my_item"]
        other_wedding = WeddingFactory(company=user.company)
        payload = {"name": "Novo Nome", "wedding": str(other_wedding.uuid)}
        response = auth_client.patch(
            f"/api/v1/logistics/items/{item.uuid}/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 200
        item.refresh_from_db()
        assert item.name == "Novo Nome"
        assert item.wedding.uuid == seed_data["my_item"].wedding.uuid

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
        response = auth_client.post(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/upload/",
            data=json.dumps({"pdf_file_key": "contracts/test.pdf"}),
            content_type="application/json",
        )
        assert response.status_code == 200

    def test_delete_contract_file(self, auth_client, seed_data):
        auth_client.post(
            f"/api/v1/logistics/contracts/{seed_data['my_contract'].uuid}/upload/",
            data=json.dumps({"pdf_file_key": "contracts/test.pdf"}),
            content_type="application/json",
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


class DummyStorageService:
    def generate_presigned_put_url(
        self, bucket: str, object_key: str, content_type: str, expires_in: int = 900
    ) -> str:
        return f"https://r2.com/{bucket}/{object_key}"


@pytest.mark.django_db
class TestContractCreateFullAPI:
    """Testes HTTP do endpoint contracts/full/ (criação atômica)."""

    def _wedding_supplier(self, user):
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        return wedding, supplier

    def _category(self, user):
        wedding = WeddingFactory(company=user.company)
        budget = BudgetFactory(wedding=wedding)
        category = BudgetCategoryFactory(budget=budget)
        return wedding, category

    def test_create_full_contract_only(self, auth_client, user):
        """POST /full/ apenas com dados do contrato retorna 201."""
        wedding, supplier = self._wedding_supplier(user)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato Full",
                    "total_amount": "5000.00",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Contrato Full"
        assert "uuid" in data

    def test_create_full_with_items(self, auth_client, user):
        """POST /full/ com items_data em JSON string retorna 201."""
        wedding, supplier = self._wedding_supplier(user)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato com Itens",
                    "total_amount": "3000.00",
                    "items_data": (
                        '[{"name":"Item A","quantity":2,'
                        '"acquisition_status":"PENDING"}]'
                    ),
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["name"] == "Contrato com Itens"

    def test_create_full_with_file(self, auth_client, user):
        """POST /full/ com pdf_file_key retorna 201."""
        wedding, supplier = self._wedding_supplier(user)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato com PDF",
                    "total_amount": "7000.00",
                    "pdf_file_key": "contracts/contrato.pdf",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["has_file"] is True
        assert data["file_name"] == "contrato.pdf"

    def test_create_full_with_expense(self, auth_client, user):
        """POST /full/ com create_expense=True cria despesa vinculada."""
        wedding, category = self._category(user)
        supplier = SupplierFactory(company=user.company)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato com Despesa",
                    "total_amount": "5000.00",
                    "create_expense": True,
                    "expense_category": str(category.uuid),
                    "expense_num_installments": 2,
                    "expense_first_due_date": "2026-12-25",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["expense_uuid"] is not None

    def test_create_full_with_all(self, auth_client, user):
        """POST /full/ com file + items + expense — cenário completo."""
        wedding, category = self._category(user)
        supplier = SupplierFactory(company=user.company)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato Completo",
                    "total_amount": "10000.00",
                    "description": "Teste full",
                    "status": "DRAFT",
                    "items_data": (
                        '[{"name":"Item 1","quantity":10,'
                        '"acquisition_status":"PENDING"}]'
                    ),
                    "create_expense": True,
                    "expense_category": str(category.uuid),
                    "expense_num_installments": 3,
                    "expense_first_due_date": "2026-12-25",
                    "pdf_file_key": "contracts/contrato.pdf",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Contrato Completo"

    def test_create_full_invalid_items_json(self, auth_client, user):
        """POST /full/ com items_data inválido retorna 422."""
        wedding, supplier = self._wedding_supplier(user)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato",
                    "total_amount": "5000.00",
                    "items_data": "{invalid json",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 422
        body = response.json()
        detail = str(body.get("detail", ""))
        assert "json" in detail.lower()

    def test_create_full_expense_without_category(self, auth_client, user):
        """POST /full/ com create_expense=True sem categoria retorna 422."""
        wedding = WeddingFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Contrato",
                    "total_amount": "5000.00",
                    "create_expense": True,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 422

    def test_create_full_multitenancy(self, auth_client, user):
        """Usuário não pode criar contrato com wedding de outro tenant."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(company=other_user.company)
        supplier = SupplierFactory(company=user.company)
        response = auth_client.post(
            "/api/v1/logistics/contracts/full/",
            data=json.dumps(
                {
                    "wedding": str(other_wedding.uuid),
                    "supplier": str(supplier.uuid),
                    "name": "Cross Tenant",
                    "total_amount": "1000.00",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_generate_upload_url_api_success(
        self, auth_client, user, settings
    ):
        settings.AWS_STORAGE_BUCKET_NAME = "test-bucket"
        wedding = WeddingFactory(company=user.company)

        from apps.logistics.services.contract_service import ContractService

        original_storage = ContractService._storage_service
        dummy_storage = DummyStorageService()
        ContractService.set_storage_service(dummy_storage)

        try:
            response = auth_client.post(
                "/api/v1/logistics/contracts/upload-url/",
                data=json.dumps(
                    {
                        "filename": "contrato.pdf",
                        "wedding_id": str(wedding.uuid),
                    }
                ),
                content_type="application/json",
            )
            assert response.status_code == 200
            data = response.json()
            assert "upload_url" in data
            assert "object_key" in data
            assert data["upload_url"] == f"https://r2.com/test-bucket/{data['object_key']}"
        finally:
            ContractService.set_storage_service(original_storage)


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
