import pytest

from apps.events.tests.factories import EventFactory
from apps.finances.tests.factories import BudgetFactory


@pytest.mark.django_db
@pytest.mark.api
class TestBudgetAPI:
    """Testes de integração para a API de Orçamentos - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_budgets_isolation(self, auth_client, finance_seed):
        """Garante que um planner só vê orçamentos dos seus casamentos."""
        response = auth_client.get("/api/v1/finances/budgets/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["uuid"] == str(finance_seed["my_budget"].uuid)

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_budget_forbidden(self, auth_client, finance_seed):
        """Segurança: Não pode acessar orçamento alheio."""
        other_budget = finance_seed["other_budget"]
        response = auth_client.get(f"/api/v1/finances/budgets/{other_budget.uuid}/")
        assert response.status_code == 404

    def test_get_budget_for_event_lazy_loading(self, auth_client, user):
        """Valida o fluxo vital de lazy loading via API."""
        event = EventFactory(company=user.company)
        # O event recém-criado não tem budget
        url = f"/api/v1/finances/budgets/for-event/{event.uuid}/"
        response = auth_client.get(url)
        assert response.status_code == 200
        # O Django Ninja converte Decimal p/ string ou int dependendo da config.
        # Ajustamos para aceitar o valor numérico bruto.
        assert float(response.json()["total_estimated"]) == 0.0

    def test_update_budget_success(self, auth_client, finance_seed):
        """Cenário feliz de atualização."""
        budget = finance_seed["my_budget"]
        response = auth_client.patch(
            f"/api/v1/finances/budgets/{budget.uuid}/",
            data={"total_estimated": "75000.00"},
            content_type="application/json",
        )
        assert response.status_code == 200
        assert float(response.json()["total_estimated"]) == 75000.00

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_budget_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode atualizar orçamento alheio."""
        other_budget = finance_seed["other_budget"]
        response = auth_client.patch(
            f"/api/v1/finances/budgets/{other_budget.uuid}/",
            data={"total_estimated": "999.00"},
            content_type="application/json",
        )
        assert response.status_code == 404

    def test_delete_budget_success(self, auth_client, user):
        """Cenário feliz de deleção. Usamos um budget vazio para evitar 409."""
        event = EventFactory(company=user.company)
        # Usamos a Factory para criar um budget isolado e limpo
        budget = BudgetFactory(event=event, total_estimated=1000)

        response = auth_client.delete(f"/api/v1/finances/budgets/{budget.uuid}/")
        assert response.status_code == 204
