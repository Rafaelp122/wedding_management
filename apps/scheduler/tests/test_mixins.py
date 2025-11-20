"""
Testes para os mixins do app scheduler.
"""
from datetime import timedelta
from unittest.mock import Mock

from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.scheduler.mixins import (
    EventFormLayoutMixin,
    EventFormMixin,
    EventHtmxResponseMixin,
    EventModalContextMixin,
    EventOwnershipMixin,
)
from apps.scheduler.models import Event
from apps.scheduler.forms import EventForm
from apps.users.models import User
from apps.weddings.models import Wedding


class EventOwnershipMixinTest(TestCase):
    """Testes para EventOwnershipMixin."""

    def setUp(self):
        """Configuração inicial."""
        self.mixin = EventOwnershipMixin()
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass123"
        )

        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            budget=50000.00,
        )

        self.event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Teste",
            start_time=timezone.now() + timedelta(days=7),
        )

        # Configurar mixin
        self.request = self.factory.get("/")
        self.request.user = self.user
        self.mixin.request = self.request
        self.mixin.wedding = self.wedding

    def test_get_event_or_404_success(self):
        """Testa obtenção de evento com sucesso."""
        event = self.mixin.get_event_or_404(self.event.id)

        self.assertEqual(event, self.event)

    def test_get_event_or_404_not_found(self):
        """Testa obtenção de evento inexistente."""
        with self.assertRaises(Http404):
            self.mixin.get_event_or_404(99999)

    def test_get_event_or_404_wrong_wedding(self):
        """Testa obtenção de evento de outro casamento."""
        other_wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Pedro",
            bride_name="Ana",
            date=timezone.now().date() + timedelta(days=200),
            budget=40000.00,
        )

        self.mixin.wedding = other_wedding

        with self.assertRaises(Http404):
            self.mixin.get_event_or_404(self.event.id)


class EventHtmxResponseMixinTest(TestCase):
    """Testes para EventHtmxResponseMixin."""

    def setUp(self):
        """Configuração inicial."""
        self.mixin = EventHtmxResponseMixin()
        self.factory = RequestFactory()

    def test_get_htmx_success_response(self):
        """Testa resposta de sucesso HTMX."""
        # Adicionar request ao mixin
        request = self.factory.get("/")
        request.user = Mock(username="testuser")
        self.mixin.request = request

        response = self.mixin.render_event_saved_response()

        self.assertEqual(response.status_code, 204)
        self.assertIn("HX-Trigger", response.headers)
        self.assertEqual(response.headers["HX-Trigger"], "eventSaved")

    def test_get_htmx_delete_response(self):
        """Testa resposta de deleção HTMX."""
        # Adicionar request ao mixin
        request = self.factory.get("/")
        request.user = Mock(username="testuser")
        self.mixin.request = request

        response = self.mixin.render_event_deleted_response(event_id=5)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Verificar conteúdo JSON
        import json

        data = json.loads(response.content)
        self.assertEqual(data.get("id"), 5)
        self.assertIn("HX-Trigger", response.headers)


class EventModalContextMixinTest(TestCase):
    """Testes para EventModalContextMixin."""

    def test_inherits_from_modal_context_mixin(self):
        """Testa que herda de ModalContextMixin do core."""
        from apps.core.mixins.views import ModalContextMixin

        self.assertTrue(
            issubclass(EventModalContextMixin, ModalContextMixin)
        )


class EventFormLayoutMixinTest(TestCase):
    """Testes para EventFormLayoutMixin."""

    def setUp(self):
        """Configuração inicial."""
        self.mixin = EventFormLayoutMixin()

    def test_inherits_from_form_layout_mixin(self):
        """Testa que herda de FormLayoutMixin do core."""
        from apps.core.mixins.forms import FormLayoutMixin

        self.assertTrue(issubclass(EventFormLayoutMixin, FormLayoutMixin))

    def test_has_form_class(self):
        """Testa que define form_class."""
        self.assertEqual(self.mixin.form_class, EventForm)

    def test_has_form_layout_dict(self):
        """Testa que define form_layout_dict."""
        self.assertIsNotNone(self.mixin.form_layout_dict)
        self.assertIn("title", self.mixin.form_layout_dict)
        self.assertIn("event_type", self.mixin.form_layout_dict)

    def test_has_form_icons(self):
        """Testa que define form_icons."""
        self.assertIsNotNone(self.mixin.form_icons)
        self.assertIn("title", self.mixin.form_icons)
        self.assertIn("location", self.mixin.form_icons)


class EventFormMixinTest(TestCase):
    """Testes para EventFormMixin."""

    def setUp(self):
        """Configuração inicial."""
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass123"
        )

        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            budget=50000.00,
        )

        self.mixin = EventFormMixin()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = self.user
        self.mixin.request = self.request
        self.mixin.wedding = self.wedding

    def test_has_form_class(self):
        """Testa que define form_class."""
        self.assertEqual(self.mixin.form_class, EventForm)

    def test_form_valid_saves_event(self):
        """Testa que form_valid salva evento com planner e wedding."""
        # Criar um form válido
        from datetime import date

        form_data = {
            "title": "Test Event",
            "event_type": Event.TypeChoices.MEETING,
            "event_date": date.today(),
            "start_time_input": "14:00",
        }

        form = EventForm(data=form_data)

        self.assertTrue(form.is_valid())

        # Adicionar método render_event_saved_response ao mixin
        self.mixin.render_event_saved_response = Mock(
            return_value=HttpResponse(status=204)
        )

        response = self.mixin.form_valid(form)

        # Verificar que evento foi salvo
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertEqual(event.planner, self.user)
        self.assertEqual(event.wedding, self.wedding)
        self.assertEqual(response.status_code, 204)
