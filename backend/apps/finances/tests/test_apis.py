import pytest

from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.weddings.services import WeddingService


@pytest.fixture
def seed_data(user, django_user_model):
    # Planner alvo
    my_wedding = WeddingService.create(
        user,
        {
            "bride_name": "Minha",
            "groom_name": "Noz",
            "location": "A",
            "date": "2026-10-11",
        },
    )
    my_budget = BudgetService.get_or_create_for_wedding(user, my_wedding.uuid)
    my_category = my_budget.categories.first()
    my_expense = ExpenseService.create(
        user,
        {
            "category": my_category,
            "description": "Despesa A",
            "estimated_amount": "100.00",
            "actual_amount": "0.00",
        },
    )

    # Planner alheio
    other_user = django_user_model.objects.create_user(email="b@b.com", password="123")
    other_wedding = WeddingService.create(
        other_user,
        {
            "bride_name": "Outra",
            "groom_name": "Outro",
            "location": "B",
            "date": "2026-10-11",
        },
    )
    other_budget = BudgetService.get_or_create_for_wedding(
        other_user, other_wedding.uuid
    )
    other_category = other_budget.categories.first()
    ExpenseService.create(
        other_user,
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
