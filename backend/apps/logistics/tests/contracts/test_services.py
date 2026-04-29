from unittest.mock import patch

import pytest
from django.db.models import ProtectedError

from apps.core.exceptions import DomainIntegrityError
from apps.events.tests.factories import EventFactory
from apps.finances.tests.factories import BudgetCategoryFactory
from apps.logistics.models import Contract
from apps.logistics.services.contract_service import ContractService
from apps.logistics.tests.factories import ContractFactory, SupplierFactory


@pytest.mark.django_db
@pytest.mark.service
class TestContractService:
    """Testes de lógica de negócio para o ContractService - Foco em Cobertura."""

    def test_list_contracts_with_filter(self, user):
        event = EventFactory(company=user.company)
        ContractFactory(event=event)
        ContractFactory(event=event)
        # Outro event do mesmo planner. Passamos o event via factory.
        other_event = EventFactory(company=user.company)
        ContractFactory(event=other_event)

        qs = ContractService.list(user, event_id=event.uuid)
        assert qs.count() == 2

    def test_create_contract_with_category(self, user):
        event = EventFactory(company=user.company)
        supplier = SupplierFactory(company=user.company)
        category = BudgetCategoryFactory(event=event)

        data = {
            "event": event.uuid,
            "supplier": supplier.uuid,
            "budget_category": category.uuid,
            "total_amount": 1000,
        }
        contract = ContractService.create(user, data)
        assert contract.budget_category == category

    def test_update_contract_full(self, user):
        event = EventFactory(company=user.company)
        contract = ContractFactory(event=event, pdf_file="old.pdf")
        new_supplier = SupplierFactory(company=user.company)
        new_category = BudgetCategoryFactory(event=contract.event)

        data = {
            "supplier": new_supplier.uuid,
            "budget_category": new_category.uuid,
            "total_amount": 9999,
            "pdf_file": None,  # Deve ser ignorado pelo service
        }

        updated = ContractService.update(user, contract, data)
        assert updated.supplier == new_supplier
        assert updated.budget_category == new_category
        assert updated.total_amount == 9999
        assert updated.pdf_file == "old.pdf"  # Não mudou para None

    def test_delete_contract_protected_error(self, user):
        event = EventFactory(company=user.company)
        contract = ContractFactory(event=event)

        # Simulamos um erro de proteção injetando uma falha no delete real
        with pytest.raises(DomainIntegrityError):
            with patch.object(
                Contract, "delete", side_effect=ProtectedError("Erro", [])
            ):
                ContractService.delete(contract)
