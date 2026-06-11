from uuid import uuid4

import pytest

from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.weddings.services import WeddingService


@pytest.fixture
def seed_data(user, django_user_model):
    # Planner alvo
    my_wedding = WeddingService.create(
        user.company,
        {
            "bride_name": "Minha",
            "groom_name": "Noz",
            "location": "A",
            "date": "2026-10-11",
        },
    )
    my_budget = BudgetService.get_or_create_for_wedding(user.company, my_wedding.uuid)
    my_category = my_budget.categories.first()
    my_expense = ExpenseService.create(
        user.company,
        {
            "category": my_category,
            "name": "Despesa A",
            "estimated_amount": "100.00",
            "actual_amount": "100.00",
        },
    )

    # Planner alheio
    from apps.users.tests.factories import UserFactory

    other_user = UserFactory(email="b@b.com")
    other_user.set_password("123")
    other_user.save()

    other_wedding = WeddingService.create(
        other_user.company,
        {
            "bride_name": "Alheia",
            "groom_name": "Alheio",
            "location": "B",
            "date": "2026-10-11",
        },
    )
    other_budget = BudgetService.get_or_create_for_wedding(
        other_user.company, other_wedding.uuid
    )
    other_category = other_budget.categories.first()
    ExpenseService.create(
        other_user.company,
        {
            "category": other_category,
            "name": "Despesa B",
            "estimated_amount": "200.00",
            "actual_amount": "200.00",
        },
    )

    return {
        "my_budget": my_budget,
        "my_category": my_category,
        "my_expense": my_expense,
    }


@pytest.mark.django_db
class TestFinancesNinjaAPI:
    def test_list_budgets_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/finances/budgets/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["uuid"] == str(seed_data["my_budget"].uuid)
        assert data["items"][0]["total_estimated"] == "0.00"

    def test_list_categories_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/finances/categories/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 6

    def test_list_expenses_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/finances/expenses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["name"] == "Despesa A"

    def test_list_installments_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/finances/installments/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1  # 1 parcela auto-gerada (min 1)

    def test_update_expense_returns_422_on_business_rule_violation(
        self, auth_client, seed_data
    ):
        expense_uuid = seed_data["my_expense"].uuid

        response = auth_client.patch(
            f"/api/v1/finances/expenses/{expense_uuid}/",
            data={"name": ""},
            content_type="application/json",
        )

        assert response.status_code == 422

    def test_update_budget_success(self, auth_client, seed_data):
        """PATCH orçamento — altera total_estimated com sucesso."""
        response = auth_client.patch(
            f"/api/v1/finances/budgets/{seed_data['my_budget'].uuid}/",
            data={"total_estimated": "50000.00"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["total_estimated"] == "50000.00"

    def test_create_category_success(self, auth_client, seed_data):
        """POST categoria — cria nova categoria no orçamento."""
        # Aumenta teto do orçamento primeiro (está em 0.00)
        auth_client.patch(
            f"/api/v1/finances/budgets/{seed_data['my_budget'].uuid}/",
            data={"total_estimated": "10000.00"},
            content_type="application/json",
        )
        payload = {
            "name": "Buffet Extra",
            "description": "",
            "budget": str(seed_data["my_budget"].uuid),
            "allocated_budget": "5000.00",
        }
        response = auth_client.post(
            "/api/v1/finances/categories/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201, response.json()
        assert response.json()["name"] == "Buffet Extra"

    def test_update_category_success(self, auth_client, seed_data):
        """PATCH categoria — altera nome com sucesso."""
        response = auth_client.patch(
            f"/api/v1/finances/categories/{seed_data['my_category'].uuid}/",
            data={"name": "Buffet Premium"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Buffet Premium"

    def test_delete_category_success(self, auth_client, seed_data):
        """DELETE categoria — remove categoria recém-criada (sem despesas)."""
        # Aumenta teto do orçamento primeiro
        auth_client.patch(
            f"/api/v1/finances/budgets/{seed_data['my_budget'].uuid}/",
            data={"total_estimated": "10000.00"},
            content_type="application/json",
        )
        payload = {
            "name": "Para Deletar",
            "description": "",
            "budget": str(seed_data["my_budget"].uuid),
            "allocated_budget": "1000.00",
        }
        create_resp = auth_client.post(
            "/api/v1/finances/categories/",
            data=payload,
            content_type="application/json",
        )
        new_uuid = create_resp.json()["uuid"]

        response = auth_client.delete(f"/api/v1/finances/categories/{new_uuid}/")
        assert response.status_code == 204

    def test_update_expense_success(self, auth_client, seed_data):
        """PATCH despesa — altera nome com sucesso."""
        response = auth_client.patch(
            f"/api/v1/finances/expenses/{seed_data['my_expense'].uuid}/",
            data={"name": "Despesa Atualizada"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Despesa Atualizada"

    def test_delete_expense_success(self, auth_client, seed_data):
        """DELETE despesa — remove com sucesso."""
        response = auth_client.delete(
            f"/api/v1/finances/expenses/{seed_data['my_expense'].uuid}/",
        )
        assert response.status_code == 204

    def test_mark_installment_as_paid_success(self, auth_client, seed_data):
        """POST marcar parcela como paga — status PAID."""
        installment = seed_data["my_expense"].installments.first()
        response = auth_client.post(
            f"/api/v1/finances/installments/{installment.uuid}/mark-as-paid/",
        )
        assert response.status_code == 200
        assert response.json()["status"] == "PAID"

    def test_unmark_installment_as_paid_success(self, auth_client, seed_data):
        """POST desmarcar parcela como paga — status PENDING."""
        installment = seed_data["my_expense"].installments.first()

        # Marca como paga primeiro
        auth_client.post(
            f"/api/v1/finances/installments/{installment.uuid}/mark-as-paid/",
        )

        # Desmarca
        response = auth_client.post(
            f"/api/v1/finances/installments/{installment.uuid}/unmark-as-paid/",
        )
        assert response.status_code == 200

    def test_adjust_installment_success(self, auth_client, seed_data):
        """PATCH ajustar parcela — altera valor com sucesso."""
        # Atualiza expense para 200 primeiro (Tolerância Zero exige soma = valor)
        auth_client.patch(
            f"/api/v1/finances/expenses/{seed_data['my_expense'].uuid}/",
            data={"actual_amount": "200.00"},
            content_type="application/json",
        )
        installment = seed_data["my_expense"].installments.first()
        response = auth_client.patch(
            f"/api/v1/finances/installments/{installment.uuid}/adjust/",
            data={"amount": "200.00"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert response.json()["amount"] == "200.00"

    def test_get_budget_for_wedding(self, auth_client, seed_data):
        """GET orçamento por wedding_uuid — lazy-create."""
        wedding_uuid = seed_data["my_budget"].wedding.uuid
        response = auth_client.get(
            f"/api/v1/finances/budgets/for-wedding/{wedding_uuid}/"
        )
        assert response.status_code == 200
        assert "total_estimated" in response.json()

    def test_get_expense(self, auth_client, seed_data):
        """GET despesa por UUID."""
        response = auth_client.get(
            f"/api/v1/finances/expenses/{seed_data['my_expense'].uuid}/"
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Despesa A"

    def test_get_installment(self, auth_client, seed_data):
        """GET parcela por UUID."""
        installment = seed_data["my_expense"].installments.first()
        response = auth_client.get(f"/api/v1/finances/installments/{installment.uuid}/")
        assert response.status_code == 200
        assert "amount" in response.json()

    def test_from_document(self, auth_client, seed_data):
        """POST from-document — sugere payload de despesa a partir de contrato."""
        # Cria um contrato via API (precisa ter supplier + wedding)
        from apps.logistics.tests.factories import ContractFactory

        wedding = seed_data["my_budget"].wedding
        from apps.logistics.tests.factories import SupplierFactory

        supplier = SupplierFactory(company=wedding.company)
        contract = ContractFactory(wedding=wedding, supplier=supplier)

        response = auth_client.post(
            f"/api/v1/finances/expenses/from-document/{contract.uuid}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert "description" in data


@pytest.mark.django_db
class TestFinancesAPIErrorHandling:
    def test_get_budget_not_found(self, auth_client):
        response = auth_client.get(f"/api/v1/finances/budgets/{uuid4()}/")
        assert response.status_code == 404

    def test_get_category_not_found(self, auth_client):
        response = auth_client.get(f"/api/v1/finances/categories/{uuid4()}/")
        assert response.status_code == 404

    def test_get_expense_not_found(self, auth_client):
        response = auth_client.get(f"/api/v1/finances/expenses/{uuid4()}/")
        assert response.status_code == 404
