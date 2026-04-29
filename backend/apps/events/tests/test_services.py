from unittest.mock import patch

import pytest
from django.core.exceptions import ValidationError

from apps.core.exceptions import BusinessRuleViolation, DomainIntegrityError
from apps.events.models import Event
from apps.events.services.event_service import EventService
from apps.events.tests.factories import EventFactory, WeddingFactory
from apps.logistics.tests.factories import ContractFactory


@pytest.mark.django_db
@pytest.mark.service
class TestEventService:
    """
    Testes de lógica de negócio pura (Service Layer).
    """

    def test_list_events_returns_filtered_queryset(self, user):
        """RF: list() deve retornar apenas casamentos da empresa logada."""
        EventFactory(company=user.company)
        EventFactory()  # Outra empresa

        queryset = EventService.list(user=user)

        assert queryset.count() == 1
        assert all(w.company == user.company for w in queryset)

    def test_create_event_success(self, user, event_payload):
        """Garante criação bem sucedida e limpeza de campos extras."""
        event_payload["invalid_field"] = "hack"

        event = EventService.create(user=user, data=event_payload)

        assert event.company == user.company
        assert Event.objects.count() == 1

    def test_update_event_success(self, user):
        """Garante atualização bem sucedida da instância e detalhes."""
        event = WeddingFactory(company=user.company, bride_name="Original")
        update_data = {"wedding_detail": {"bride_name": "Atualizada"}}

        updated_event = EventService.update(user=user, instance=event, data=update_data)
        updated_event.refresh_from_db()

        assert updated_event.wedding_detail.bride_name == "Atualizada"

    def test_create_event_fail_fast_validation_error(self, user, event_payload):
        """Cenário: Dados inválidos (negativos) disparam ValidationError."""
        event_payload["expected_guests"] = -10

        with pytest.raises(ValidationError):
            EventService.create(user=user, data=event_payload)

    def test_service_create_transaction_rollback_on_error(self, user, event_payload):
        """Garante atomicidade: nada é salvo se houver erro no processo."""

        class DatabaseError(Exception):
            pass

        with patch.object(Event, "save", side_effect=DatabaseError("Database Crash")):
            with pytest.raises(DatabaseError):
                EventService.create(user=user, data=event_payload)

        assert Event.objects.count() == 0

    def test_completed_status_constraint_is_enforced_in_update(self, user):
        """Regra de Negócio: Não pode concluir evento futuro via update."""
        from datetime import date, timedelta

        future_date = date.today() + timedelta(days=100)
        event = EventFactory(company=user.company, date=future_date)

        update_data = {"status": Event.StatusChoices.COMPLETED}

        with pytest.raises(
            BusinessRuleViolation, match="Não pode marcar como CONCLUÍDO"
        ):
            EventService.update(user=user, instance=event, data=update_data)

    def test_delete_event_protected_by_contracts(self, user):
        """Proteção de Integridade: Impede deleção com contratos vinculados."""
        event = EventFactory(company=user.company)
        ContractFactory(event=event)

        with pytest.raises(DomainIntegrityError):
            EventService.delete(instance=event)

    def test_delete_event_full_clean_cascade(self, user, event_payload):
        """Garante deleção total (Hard Delete) e limpeza em cascata."""
        event = EventService.create(user=user, data=event_payload)
        EventService.delete(instance=event)
        assert Event.objects.count() == 0

    def test_create_wedding_dispatches_signal(self, user, event_payload):
        """
        Efeito Colateral: BudgetService deve ser chamado via Signal
        ao criar casamento.
        """
        with patch(
            "apps.finances.services.budget_service.BudgetService.setup_initial_budget"
        ) as mock_setup:
            EventService.create(user=user, data=event_payload)

        assert mock_setup.called
