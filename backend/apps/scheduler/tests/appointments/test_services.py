from datetime import timedelta
from uuid import uuid4

import pytest
from django.utils import timezone

from apps.core.exceptions import BusinessRuleViolation, ObjectNotFoundError
from apps.scheduler.models import Event
from apps.scheduler.services.events import EventService
from apps.scheduler.tests.factories import EventFactory
from apps.users.tests.factories import UserFactory
from apps.weddings.tests.factories import WeddingFactory


@pytest.mark.django_db
class TestEventServiceCreate:
    """Testes de criação de eventos via EventService."""

    def test_create_event_success(self, user):
        """Criação de evento vinculado ao casamento."""
        wedding = WeddingFactory(user_context=user)
        now = timezone.now()

        data = {
            "wedding": wedding.uuid,
            "title": "Prova de Vestido",
            "event_type": Event.TypeChoices.MEETING,
            "start_time": now + timedelta(days=30),
        }

        event = EventService.create(user.company, data)

        assert event.wedding == wedding
        assert event.title == "Prova de Vestido"
        assert event.company == user.company

    def test_create_event_with_wedding_instance(self, user):
        """create() aceita instância de Wedding, não só UUID."""
        wedding = WeddingFactory(user_context=user)

        data = {
            "wedding": wedding,
            "title": "Reunião com Buffet",
            "event_type": Event.TypeChoices.VISIT,
            "start_time": timezone.now() + timedelta(days=15),
        }

        event = EventService.create(user.company, data)
        assert event.wedding == wedding

    def test_create_event_wedding_not_found(self, user):
        """UUID de wedding inexistente levanta ObjectNotFoundError."""
        data = {
            "wedding": uuid4(),
            "title": "Evento Fantasma",
            "event_type": Event.TypeChoices.OTHER,
            "start_time": timezone.now() + timedelta(days=1),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            EventService.create(user.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    def test_create_event_multitenancy(self):
        """Usuário A não pode criar evento com wedding do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)

        data = {
            "wedding": wedding_b.uuid,
            "title": "Invasão",
            "event_type": Event.TypeChoices.OTHER,
            "start_time": timezone.now() + timedelta(days=1),
        }

        with pytest.raises(ObjectNotFoundError) as exc_info:
            EventService.create(user_a.company, data)

        assert "wedding_not_found_or_denied" in str(exc_info.value.code)

    def test_create_payment_event_blocked(self, user):
        """BR-S01: Eventos PAYMENT não podem ser criados manualmente."""
        wedding = WeddingFactory(user_context=user)

        data = {
            "wedding": wedding.uuid,
            "title": "Pagamento Manual",
            "event_type": Event.TypeChoices.PAYMENT,
            "start_time": timezone.now() + timedelta(days=30),
        }

        with pytest.raises(BusinessRuleViolation) as exc_info:
            EventService.create(user.company, data)

        assert exc_info.value.code == "payment_event_readonly"
        assert Event.objects.count() == 0

    def test_create_payment_event_internal_allowed(self, user):
        """BR-S01: Chamadas internas (_caller_internal=True) podem criar PAYMENT."""
        wedding = WeddingFactory(user_context=user)

        data = {
            "wedding": wedding.uuid,
            "title": "Pagamento: Buffet - Parcela 1/3",
            "event_type": Event.TypeChoices.PAYMENT,
            "start_time": timezone.now() + timedelta(days=30),
        }

        event = EventService.create(user.company, data, _caller_internal=True)

        assert event.event_type == Event.TypeChoices.PAYMENT
        assert event.title == "Pagamento: Buffet - Parcela 1/3"


@pytest.mark.django_db
class TestEventServiceUpdate:
    """Testes de atualização de eventos via EventService."""

    def test_update_event_title(self, user):
        """Atualização de título é permitida."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Título Antigo")

        updated = EventService.update(user.company, event, {"title": "Título Novo"})

        assert updated.title == "Título Novo"

    def test_update_event_cannot_change_wedding(self, user):
        """Wedding é bloqueado no update."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding1)

        updated = EventService.update(user.company, event, {"wedding": wedding2.uuid})

        assert updated.wedding == wedding1

    def test_update_event_toggle_reminder(self, user):
        """Habilitar/desabilitar lembrete é permitido."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, reminder_enabled=False)

        updated = EventService.update(user.company, event, {"reminder_enabled": True})

        assert updated.reminder_enabled is True

    def test_update_cannot_change_event_type_to_payment(self, user):
        """BR-S01: Não pode alterar event_type de um evento para PAYMENT."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.MEETING,
            title="Reunião Normal",
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            EventService.update(
                user.company, event, {"event_type": Event.TypeChoices.PAYMENT}
            )

        assert exc_info.value.code == "payment_event_readonly"

    def test_update_payment_event_blocked(self, user):
        """BR-S01: Eventos PAYMENT não podem ser editados manualmente."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            title="Pagamento: Buffet - Parcela 1/3",
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            EventService.update(user.company, event, {"title": "Novo título"})

        assert exc_info.value.code == "payment_event_readonly"

    def test_update_payment_event_all_fields_blocked(self, user):
        """BR-S01: Nenhum campo de evento PAYMENT pode ser alterado."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            title="Pagamento: Decoração - Parcela 2/5",
        )

        with pytest.raises(BusinessRuleViolation):
            EventService.update(
                user.company, event, {"start_time": timezone.now() + timedelta(days=10)}
            )

    def test_update_non_payment_event_allowed(self, user):
        """Eventos não-PAYMENT podem ser editados normalmente."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.MEETING,
            title="Reunião com Buffet",
        )

        updated = EventService.update(
            user.company, event, {"title": "Reunião com Buffet Atualizada"}
        )

        assert updated.title == "Reunião com Buffet Atualizada"

    def test_update_event_cross_tenant(self, user):
        """Evento de outro tenant não pode ser atualizado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        other_event = EventFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            EventService.update(
                user.company, other_event, {"title": "Hack"}
            )


@pytest.mark.django_db
class TestEventServiceDelete:
    """Testes de deleção de eventos via EventService."""

    def test_delete_event_success(self, user):
        """Deleção de evento sem dependências é permitida."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding)

        EventService.delete(user.company, instance=event)

        assert Event.objects.filter(uuid=event.uuid).count() == 0

    def test_delete_payment_event_blocked(self, user):
        """BR-S01: Eventos PAYMENT não podem ser deletados manualmente."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.PAYMENT,
            title="Pagamento: Buffet - Parcela 1/3",
        )

        with pytest.raises(BusinessRuleViolation) as exc_info:
            EventService.delete(user.company, instance=event)

        assert exc_info.value.code == "payment_event_readonly"
        assert Event.objects.filter(uuid=event.uuid).exists()

    def test_delete_non_payment_event_allowed(self, user):
        """Eventos não-PAYMENT podem ser deletados normalmente."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(
            wedding=wedding,
            event_type=Event.TypeChoices.MEETING,
        )

        EventService.delete(user.company, instance=event)

        assert Event.objects.filter(uuid=event.uuid).count() == 0

    def test_delete_event_cross_tenant(self, user):
        """Evento de outro tenant não pode ser deletado."""
        other_user = UserFactory()
        other_wedding = WeddingFactory(user_context=other_user)
        other_event = EventFactory(wedding=other_wedding)

        with pytest.raises(ObjectNotFoundError):
            EventService.delete(user.company, instance=other_event)


@pytest.mark.django_db
class TestEventServiceListAndGet:
    """Testes de listagem e obtenção de eventos."""

    def test_list_events_multitenancy(self):
        """list() retorna apenas eventos do tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)

        EventFactory(wedding=wedding_a, title="Evento A")
        EventFactory(wedding=wedding_b, title="Evento B")

        qs_a = EventService.list(user_a.company)
        assert qs_a.count() == 1
        assert qs_a.first().title == "Evento A"

        qs_b = EventService.list(user_b.company)
        assert qs_b.count() == 1
        assert qs_b.first().title == "Evento B"

    def test_list_events_filter_by_wedding(self, user):
        """list() com wedding_id filtra por casamento."""
        wedding1 = WeddingFactory(user_context=user)
        wedding2 = WeddingFactory(user_context=user)

        EventFactory(wedding=wedding1, title="Evento W1")
        EventFactory(wedding=wedding2, title="Evento W2")

        qs = EventService.list(user.company, wedding_id=wedding1.uuid)
        assert qs.count() == 1
        assert qs.first().title == "Evento W1"

    def test_get_event_success(self, user):
        """get() retorna evento por UUID."""
        wedding = WeddingFactory(user_context=user)
        event = EventFactory(wedding=wedding, title="Degustação")

        result = EventService.get(user.company, event.uuid)
        assert result.uuid == event.uuid
        assert result.title == "Degustação"

    def test_get_event_not_found(self, user):
        """UUID inexistente levanta ObjectNotFoundError."""
        with pytest.raises(ObjectNotFoundError):
            EventService.get(user.company, uuid4())

    def test_get_event_multitenancy(self):
        """Usuário A não pode acessar evento do Usuário B."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        event_b = EventFactory(wedding=wedding_b)

        with pytest.raises(ObjectNotFoundError):
            EventService.get(user_a.company, event_b.uuid)

    def test_list_events_empty_company(self, user):
        """list() sem eventos retorna QuerySet vazio."""
        qs = EventService.list(user.company)
        assert qs.count() == 0
