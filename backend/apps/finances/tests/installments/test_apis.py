import pytest

from apps.finances.tests.factories import InstallmentFactory


@pytest.mark.django_db
@pytest.mark.api
class TestInstallmentAPI:
    """Testes de integração para a API de Parcelas - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_installments_isolation(self, auth_client, finance_seed):
        """Garante que o planner só vê parcelas das suas despesas."""
        # Cria uma parcela para a despesa do planner logado
        InstallmentFactory(expense=finance_seed["my_expense"])

        # Cria uma parcela para despesa de outro planner
        InstallmentFactory(expense=finance_seed["other_expense"])

        response = auth_client.get("/api/v1/finances/installments/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_installment_forbidden(self, auth_client, finance_seed):
        """Segurança: Não pode acessar parcela de outro planner."""
        other_inst = InstallmentFactory(expense=finance_seed["other_expense"])
        response = auth_client.get(f"/api/v1/finances/installments/{other_inst.uuid}/")
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_update_installment_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode editar parcela de outro planner."""
        other_inst = InstallmentFactory(expense=finance_seed["other_expense"])
        response = auth_client.patch(
            f"/api/v1/finances/installments/{other_inst.uuid}/",
            data={"amount": "1.00"},
            content_type="application/json",
        )
        assert response.status_code == 404

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_delete_installment_isolation(self, auth_client, finance_seed):
        """Segurança: Não pode deletar parcela de outro planner."""
        other_inst = InstallmentFactory(expense=finance_seed["other_expense"])
        response = auth_client.delete(
            f"/api/v1/finances/installments/{other_inst.uuid}/"
        )
        assert response.status_code == 404
