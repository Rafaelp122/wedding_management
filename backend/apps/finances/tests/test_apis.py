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
            "description": "Despesa A",
            "estimated_amount": "100.00",
            "actual_amount": "0.00",
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
            "bride_name": "Outra",
            "groom_name": "Noz",
            "location": "B",
            "date": "2026-10-12",
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
            "description": "Despesa B",
            "estimated_amount": "200.00",
            "actual_amount": "0.00",
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
        assert data["items"][0]["description"] == "Despesa A"

    def test_list_installments_isolation(self, auth_client, seed_data):
        response = auth_client.get("/api/v1/finances/installments/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 0

    def test_update_expense_returns_422_on_business_rule_violation(
        self, auth_client, seed_data
    ):
        expense_uuid = seed_data["my_expense"].uuid

        response = auth_client.patch(
            f"/api/v1/finances/expenses/{expense_uuid}/",
            data={"actual_amount": "10.00"},
            content_type="application/json",
        )

        assert response.status_code == 422
        payload = response.json()
        assert payload["code"] == "expense_validation_error"


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
