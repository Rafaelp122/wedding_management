from unittest.mock import patch

import pytest

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.logistics.tests.factories import ContractFactory
from apps.weddings.models import Wedding
from apps.weddings.services import WeddingService
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
@pytest.mark.service
class TestWeddingService:
    """
    Testes de lógica de negócio pura (Service Layer).
    """

    def test_list_weddings_returns_filtered_queryset(self, user):
        """RF: list() deve retornar apenas casamentos do usuário logado."""
        WeddingFactory(planner=user)
        WeddingFactory()  # Outro usuário

        queryset = WeddingService.list(user=user)

        assert queryset.count() == 1
        assert all(w.planner == user for w in queryset)

    def test_create_wedding_success(self, user, wedding_payload):
        """Garante criação bem sucedida e limpeza de campos extras."""
        wedding_payload["invalid_field"] = "hack"

        wedding = WeddingService.create(user=user, data=wedding_payload)

        assert wedding.planner == user
        assert Wedding.objects.count() == 1

    def test_update_wedding_success(self, user):
        """Garante atualização bem sucedida da instância."""
        wedding = WeddingFactory(planner=user, bride_name="Original")
        update_data = {"bride_name": "Atualizada"}

        updated_wedding = WeddingService.update(instance=wedding, data=update_data)

        assert updated_wedding.bride_name == "Atualizada"

    def test_create_wedding_fail_fast_validation_error(self, user, wedding_payload):
        """Cenário: Dados inválidos disparam BusinessRuleViolation antes do banco."""
        wedding_payload["bride_name"] = ""

        with pytest.raises(BusinessRuleViolation, match="não pode estar vazio"):
            WeddingService.create(user=user, data=wedding_payload)

    def test_create_wedding_with_negative_guests_fails(self, user, wedding_payload):
        """O serviço deve impedir convidados negativos via full_clean do Model."""
        wedding_payload["expected_guests"] = -10

        with pytest.raises(BusinessRuleViolation):
            WeddingService.create(user=user, data=wedding_payload)

    def test_service_create_transaction_rollback_on_error(self, user, wedding_payload):
        """Garante atomicidade: nada é salvo se houver erro no processo."""
        with patch.object(Wedding, "save", side_effect=Exception("Database Crash")):
            with pytest.raises(Exception, match="Database Crash"):
                WeddingService.create(user=user, data=wedding_payload)

        assert Wedding.objects.count() == 0

    def test_completed_status_constraint_is_enforced_in_update(self, user):
        """Regra de Negócio: Não pode concluir casamento futuro via update."""
        from datetime import date, timedelta

        future_date = date.today() + timedelta(days=100)
        wedding = WeddingFactory(planner=user, date=future_date)

        update_data = {"status": Wedding.StatusChoices.COMPLETED}

        with pytest.raises(
            BusinessRuleViolation, match="Não pode marcar como CONCLUÍDO"
        ):
            WeddingService.update(instance=wedding, data=update_data)

    def test_delete_wedding_protected_by_contracts(self, user):
        """Proteção de Integridade: Impede deleção com contratos vinculados."""
        wedding = WeddingFactory(planner=user)
        ContractFactory(wedding=wedding)

        with pytest.raises(DomainIntegrityError):
            WeddingService.delete(instance=wedding)

    def test_delete_wedding_full_clean_cascade(self, user, wedding_payload):
        """Garante deleção total (Hard Delete) e limpeza em cascata."""
        wedding = WeddingService.create(user=user, data=wedding_payload)
        WeddingService.delete(instance=wedding)
        assert Wedding.objects.count() == 0

    def test_create_wedding_does_not_call_budget_service(self, user, wedding_payload):
        """Efeito Colateral: Com lazy loading, BudgetService não deve ser chamado."""
        with patch(
            "apps.finances.services.budget_service.BudgetService.create"
        ) as mock_budget:
            WeddingService.create(user=user, data=wedding_payload)
        mock_budget.assert_not_called()
