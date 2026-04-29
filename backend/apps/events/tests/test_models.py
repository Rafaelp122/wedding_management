from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.events.models import Event
from apps.events.tests.factories import EventFactory, WeddingFactory


@pytest.mark.django_db
class TestEventModelIntegrity:
    def test_event_basic_creation(self, user):
        event = EventFactory(company=user.company)
        assert event.uuid is not None
        assert event.company == user.company

    def test_wedding_detail_link(self, user):
        event = WeddingFactory(company=user.company, bride_name="Maria")
        assert event.wedding_detail.bride_name == "Maria"

    def test_event_str_representation(self, user):
        event = EventFactory(company=user.company, name="Festa")
        assert "Festa" in str(event)

    def test_bride_name_max_length(self, user):
        event = WeddingFactory(company=user.company)
        detail = event.wedding_detail
        detail.bride_name = "a" * 101
        with pytest.raises(ValidationError):
            detail.full_clean()

    def test_groom_name_max_length(self, user):
        event = WeddingFactory(company=user.company)
        detail = event.wedding_detail
        detail.groom_name = "a" * 101
        with pytest.raises(ValidationError):
            detail.full_clean()


@pytest.mark.django_db
class TestEventBusinessRules:
    def test_status_completed_invalid_future_date(self, user):
        """Garante que NÃO se pode concluir um casamento que ainda não aconteceu."""
        future_date = timezone.now().date() + timedelta(days=365)
        event = EventFactory.build(
            company=user.company, date=future_date, status=Event.StatusChoices.COMPLETED
        )
        with pytest.raises(ValidationError) as exc:
            event.full_clean()

        assert "Não é possível concluir um evento agendado para o futuro." in str(
            exc.value
        )
