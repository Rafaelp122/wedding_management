import pytest


@pytest.mark.django_db
@pytest.mark.api
class TestExpenseAPI:
    """Testes de integração para a API de Despesas - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_expenses_isolation(self, auth_client, finance_seed):
        """Garante que o planner só vê suas próprias despesas."""
        response = auth_client.get("/api/v1/finances/expenses/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["description"] == "Despesa A"

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_expense_forbidden(self, auth_client, finance_seed):
        """Segurança: Não pode acessar despesa de outro planner."""
        other_expense = finance_seed["other_expense"]
        response = auth_client.get(f"/api/v1/finances/expenses/{other_expense.uuid}/")
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_expense_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode editar despesa de outro planner."""
        other_expense = finance_seed["other_expense"]
        response = auth_client.patch(
            f"/api/v1/finances/expenses/{other_expense.uuid}/",
            data={"description": "Hack"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_expense_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode deletar despesa de outro planner."""
        other_expense = finance_seed["other_expense"]
        response = auth_client.delete(
            f"/api/v1/finances/expenses/{other_expense.uuid}/"
        )
        assert response.status_code == 404

    def test_update_expense_returns_422_on_business_rule_violation(
        self, auth_client, finance_seed
    ):
        """Valida que erros de integridade (clean) retornam 422 na API."""
        expense_uuid = finance_seed["my_expense"].uuid
        # Tenta colocar valor que não bate com as parcelas (ADR-010)
        # Nota: no seed_data a despesa tem actual_amount=0 e 0 parcelas.
        # Se alterarmos para 10.00, o clean() falha porque 0 parcelas != 10.00.
        response = auth_client.patch(
            f"/api/v1/finances/expenses/{expense_uuid}/",
            data={"actual_amount": "10.00"},
            content_type="application/json",
        )
        assert response.status_code == 422
        assert response.json()["code"] == "expense_validation_error"
