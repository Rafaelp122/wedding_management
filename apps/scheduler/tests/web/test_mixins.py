"""
Testes para os mixins do app scheduler.

Estes testes focam em comportamento e lógica de negócio crítica,
não em configuração estática ou detalhes de implementação.

Princípios seguidos:
- Testar comportamento, não implementação
- Testar lógica de negócio e segurança (ownership)
- Testar edge cases que podem causar bugs reais
- NÃO testar configuração estática simples
- NÃO testar detalhes visuais (ícones, classes CSS)
"""

from datetime import date, timedelta
from unittest.mock import Mock

from django.http import Http404
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.scheduler.models import Event
from apps.scheduler.web.forms import EventForm
from apps.scheduler.web.mixins import (
    EventFormMixin,
    EventHtmxResponseMixin,
    EventOwnershipMixin,
)
from apps.users.models import User
from apps.weddings.models import Wedding


class EventOwnershipMixinTest(TestCase):
    """
    Testes CRÍTICOS para EventOwnershipMixin.

    Foco: Segurança e isolamento de dados entre usuários.
    """

    def setUp(self):
        """Configuração inicial."""
        self.mixin = EventOwnershipMixin()
        self.factory = RequestFactory()

        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass123"
        )

        # Data dinâmica para evitar testes quebradiços
        future_date = timezone.now().date() + timedelta(days=180)

        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date=future_date,
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
        """
        CRÍTICO: Verifica que usuário consegue acessar seu próprio evento.
        """
        event = self.mixin.get_event_or_404(self.event.id)
        self.assertEqual(event, self.event)

    def test_get_event_or_404_not_found(self):
        """
        CRÍTICO: Verifica que evento inexistente retorna 404.
        Edge case importante para evitar 500 errors.
        """
        with self.assertRaises(Http404):
            self.mixin.get_event_or_404(99999)

    def test_get_event_or_404_wrong_wedding(self):
        """
        CRÍTICO (SEGURANÇA): Verifica isolamento de dados.
        Usuário não pode acessar evento de outro wedding,
        mesmo que seja dele.
        """
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

    def test_get_event_or_404_wrong_user(self):
        """
        CRÍTICO (SEGURANÇA): Verifica isolamento entre usuários.
        Usuário não pode acessar evento de outro usuário.
        """
        other_user = User.objects.create_user(
            username="other", email="other@test.com", password="testpass123"
        )

        self.request.user = other_user

        with self.assertRaises(Http404):
            self.mixin.get_event_or_404(self.event.id)


class EventHtmxResponseMixinTest(TestCase):
    """
    Testes para EventHtmxResponseMixin.

    Foco: Respostas HTMX corretas (status codes e triggers).
    """

    def setUp(self):
        """Configuração inicial."""
        self.mixin = EventHtmxResponseMixin()
        self.factory = RequestFactory()

    def test_render_event_saved_response(self):
        """
        IMPORTANTE: Verifica resposta de sucesso após salvar evento.
        Frontend depende deste comportamento.
        """
        # Adicionar request ao mixin
        request = self.factory.get("/")
        request.user = Mock(username="testuser")
        self.mixin.request = request

        response = self.mixin.render_event_saved_response()

        # Deve retornar 204 No Content
        self.assertEqual(response.status_code, 204)

        # Deve ter trigger HTMX para atualizar calendário
        self.assertIn("HX-Trigger", response.headers)
        self.assertEqual(response.headers["HX-Trigger"], "eventSaved")

    def test_render_event_deleted_response(self):
        """
        IMPORTANTE: Verifica resposta após deletar evento.
        Frontend precisa remover evento do calendário.
        """
        request = self.factory.get("/")
        request.user = Mock(username="testuser")
        self.mixin.request = request

        event_id = 123
        response = self.mixin.render_event_deleted_response(event_id=event_id)

        # Deve retornar 200 com JSON
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # JSON deve conter o ID do evento deletado
        import json

        data = json.loads(response.content)
        self.assertEqual(data.get("id"), event_id)

        # Deve ter trigger HTMX com ID do evento
        self.assertIn("HX-Trigger", response.headers)


class EventFormMixinTest(TestCase):
    """
    Testes para EventFormMixin.

    Foco: Lógica de salvamento com planner e wedding corretos.
    """

    def setUp(self):
        """Configuração inicial."""
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass123"
        )

        future_date = timezone.now().date() + timedelta(days=180)

        self.wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="João",
            bride_name="Maria",
            date=future_date,
            budget=50000.00,
        )

        self.mixin = EventFormMixin()
        self.factory = RequestFactory()
        self.request = self.factory.get("/")
        self.request.user = self.user
        self.mixin.request = self.request
        self.mixin.wedding = self.wedding

    def test_form_valid_saves_with_correct_relations(self):
        """
        CRÍTICO: Verifica que form_valid salva evento com
        planner e wedding corretos.

        Isso é lógica de negócio essencial - eventos devem
        pertencer ao usuário e wedding corretos.
        """
        form_data = {
            "title": "Test Event",
            "event_type": Event.TypeChoices.MEETING,
            "start_time_input": "14:00",
        }

        form = EventForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Mock do método de resposta HTMX e get_event_date
        self.mixin.render_event_saved_response = Mock(
            return_value=Mock(status_code=204)
        )
        self.mixin.get_event_date = Mock(return_value=date.today())
        self.mixin.request.GET = {"date": date.today().strftime("%Y-%m-%d")}

        response = self.mixin.form_valid(form)

        # Verifica que evento foi criado
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()

        # CRÍTICO: Verifica relações corretas
        self.assertEqual(event.planner, self.user)
        self.assertEqual(event.wedding, self.wedding)
        self.assertEqual(event.title, "Test Event")

        # Verifica que retornou resposta de sucesso
        self.assertEqual(response.status_code, 204)

    def test_form_invalid_maintains_context(self):
        """
        IMPORTANTE: Verifica que formulário inválido mantém
        contexto do modal (wedding, event).

        Edge case: usuário não perde contexto ao corrigir erros.
        """
        # Form inválido (sem título obrigatório)
        form_data = {
            "start_time_input": "14:00",
        }

        form = EventForm(data=form_data)
        self.assertFalse(form.is_valid())

        # Mock dos métodos necessários
        self.mixin.get_context_data = Mock(
            return_value={
                "form": form,
                "wedding": self.wedding,
                "event": None,
            }
        )
        self.mixin.render_to_response = Mock(return_value=Mock(status_code=200))

        self.mixin.form_invalid(form)

        # Verifica que get_context_data foi chamado com parâmetros corretos
        self.mixin.get_context_data.assert_called_once_with(
            form=form,
            wedding=self.wedding,
            event=None,
        )

        # Verifica que render_to_response foi chamado
        self.assertTrue(self.mixin.render_to_response.called)
