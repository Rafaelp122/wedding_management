import pytest

from apps.events.tests.factories import EventFactory
from apps.finances.tests.factories import BudgetCategoryFactory
from apps.logistics.tests.factories import ContractFactory, SupplierFactory


@pytest.mark.django_db
@pytest.mark.api
class TestContractAPI:
    """Testes de integração para a API de Contratos - Conforme TESTING_STANDARDS.md."""

    @pytest.mark.multitenancy
    def test_list_contracts_isolation(self, auth_client, user):
        """Garante que um planner só vê seus próprios contratos."""
        # Contrato do usuário logado
        event = EventFactory(company=user.company)
        ContractFactory(event=event)

        # Contrato de outro usuário
        ContractFactory()

        response = auth_client.get("/api/v1/logistics/contracts/")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1

    @pytest.mark.security
    @pytest.mark.multitenancy
    def test_retrieve_contract_forbidden_for_other_planner(self, auth_client):
        """Segurança: Não pode ler detalhes de contrato alheio."""
        other_contract = ContractFactory()
        response = auth_client.get(
            f"/api/v1/logistics/contracts/{other_contract.uuid}/"
        )
        assert response.status_code == 404

    def test_create_contract_full_flow(self, auth_client, user):
        """Cenário feliz de criação de contrato."""
        event = EventFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        category = BudgetCategoryFactory(event=event)

        payload = {
            "event": str(event.uuid),
            "supplier": str(supplier.uuid),
            "budget_category": str(category.uuid),
            "total_amount": "5000.00",
            "status": "DRAFT",
            "description": "Buffet Completo",
        }

        response = auth_client.post(
            "/api/v1/logistics/contracts/",
            data=payload,
            content_type="application/json",
        )
        assert response.status_code == 201
        assert response.json()["total_amount"] == "5000.00"

    @pytest.mark.multitenancy
    def test_create_contract_with_other_user_event_fails(self, auth_client, user):
        """Segurança: Não pode criar contrato para evento de outra empresa."""
        other_event = EventFactory()
        supplier = SupplierFactory(company=user.company)
        # Categoria do outro planner
        category = BudgetCategoryFactory(event=other_event)

        payload = {
            "event": str(other_event.uuid),
            "supplier": str(supplier.uuid),
            "budget_category": str(category.uuid),
            "total_amount": "1000.00",
        }

        response = auth_client.post(
            "/api/v1/logistics/contracts/",
            data=payload,
            content_type="application/json",
        )
        # O helper get_event/resolve_event deve lançar 404 pois o event é alheio
        assert response.status_code == 404

    @pytest.mark.multitenancy
    def test_delete_contract_isolation(self, auth_client, user):
        """Segurança: Não pode deletar contrato de outro planner."""
        other_contract = ContractFactory()
        response = auth_client.delete(
            f"/api/v1/logistics/contracts/{other_contract.uuid}/"
        )
        assert response.status_code == 404
