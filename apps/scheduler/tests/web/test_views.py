"""
Testes para as views do app scheduler.
"""

from datetime import date, timedelta
from typing import cast

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from apps.scheduler.models import Event
from apps.users.models import User
from apps.weddings.models import Wedding


class SchedulerViewsTestCase(TestCase):
    """Classe base para testes de views do scheduler."""

    @classmethod
    def setUpTestData(cls):
        """Configuração inicial (executado uma vez por classe)."""
        # Criar usuários
        cls.user = User.objects.create_user(
            username="testplanner",
            email="planner@test.com",
            password="testpass123",
        )

        cls.other_user = User.objects.create_user(
            username="otherplanner",
            email="other@test.com",
            password="testpass123",
        )

        # Criar casamento
        cls.wedding = Wedding.objects.create(
            planner=cls.user,
            groom_name="João",
            bride_name="Maria",
            date=timezone.now().date() + timedelta(days=180),
            budget=50000.00,
        )

    def setUp(self):
        """Configuração que precisa ser executada antes de cada teste."""
        self.client = Client()
        # Usar force_login ao invés de login (mais rápido)
        self.client.force_login(self.user)


class SchedulerPartialViewTest(SchedulerViewsTestCase):
    """Testes para SchedulerPartialView."""

    def test_scheduler_partial_view_authenticated(self):
        """Testa acesso ao calendário autenticado."""
        url = reverse("scheduler:partial_scheduler", args=[self.wedding.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "scheduler/partials/_scheduler_partial.html")
        self.assertIn("wedding", response.context)
        self.assertEqual(response.context["wedding"], self.wedding)

    def test_scheduler_partial_view_unauthenticated(self):
        """Testa acesso sem autenticação."""
        self.client.logout()

        url = reverse("scheduler:partial_scheduler", args=[self.wedding.id])
        response = self.client.get(url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)

    def test_scheduler_partial_view_wrong_owner(self):
        """Testa acesso de usuário não proprietário."""
        # Reusar usuário já criado no setUpTestData
        self.client.logout()
        self.client.force_login(self.other_user)

        url = reverse("scheduler:partial_scheduler", args=[self.wedding.id])
        response = self.client.get(url)

        # Deve retornar 403 Forbidden
        self.assertEqual(response.status_code, 403)


class EventCreateViewTest(SchedulerViewsTestCase):
    """Testes para EventCreateView."""

    def test_event_create_form_get(self):
        """Testa exibição do formulário de criação (GET)."""
        url = reverse("scheduler:event_new", args=[self.wedding.id])
        response = self.client.get(url, {"date": "2025-12-15"})

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("wedding", response.context)
        self.assertIn("modal_title", response.context)
        self.assertEqual(response.context["modal_title"], "Novo Evento")

    def test_event_create_post_valid(self):
        """Testa criação de evento com dados válidos (POST)."""
        url = reverse("scheduler:event_create", args=[self.wedding.id])

        data = {
            "title": "Reunião com Buffet",
            "location": "Restaurante Central",
            "description": "Escolher menu",
            "event_type": Event.TypeChoices.MEETING,
            "start_time_input": "14:00",
            "end_time_input": "16:00",
        }

        # Adiciona a data no GET params (simula o clique no calendário)
        url_with_date = f"{url}?date={date.today() + timedelta(days=7)}"
        response = self.client.post(url_with_date, data)

        # Deve retornar 204 com trigger HTMX
        self.assertEqual(response.status_code, 204)
        self.assertIn("HX-Trigger", response.headers)

        # Verificar que evento foi criado
        self.assertEqual(Event.objects.count(), 1)
        event = Event.objects.first()
        self.assertIsNotNone(event)
        event = cast(Event, event)  # Type narrowing for Pylance
        self.assertEqual(event.title, "Reunião com Buffet")
        self.assertEqual(event.planner, self.user)
        self.assertEqual(event.wedding, self.wedding)

    def test_event_create_post_invalid(self):
        """Testa criação com dados inválidos."""
        url = reverse("scheduler:event_create", args=[self.wedding.id])

        data = {
            "title": "",  # Campo obrigatório vazio
            "start_time_input": "14:00",
        }

        # Adiciona a data no GET params
        url_with_date = f"{url}?date={date.today()}"
        response = self.client.post(url_with_date, data)

        # Deve retornar formulário com erros
        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertTrue(response.context["form"].errors)

        # Nenhum evento deve ser criado
        self.assertEqual(Event.objects.count(), 0)


class EventDetailViewTest(SchedulerViewsTestCase):
    """Testes para EventDetailView."""

    def setUp(self):
        """Configuração adicional."""
        super().setUp()

        self.event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Teste",
            location="Local Teste",
            description="Descrição teste",
            event_type=Event.TypeChoices.MEETING,
            start_time=timezone.now() + timedelta(days=7),
        )

    def test_event_detail_view(self):
        """Testa visualização de detalhes do evento."""
        url = reverse("scheduler:event_detail", args=[self.wedding.id, self.event.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "scheduler/partials/_event_detail.html")
        self.assertIn("event", response.context)
        self.assertEqual(response.context["event"], self.event)

    def test_event_detail_wrong_owner(self):
        """Testa acesso ao detalhe por usuário errado."""
        # Reusar usuário já criado no setUpTestData
        self.client.logout()
        self.client.force_login(self.other_user)

        url = reverse("scheduler:event_detail", args=[self.wedding.id, self.event.id])
        response = self.client.get(url)

        # Deve retornar 403 (wedding não pertence ao usuário)
        self.assertEqual(response.status_code, 403)


class EventUpdateViewTest(SchedulerViewsTestCase):
    """Testes para EventUpdateView."""

    def setUp(self):
        """Configuração adicional."""
        super().setUp()

        self.event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento Original",
            start_time=timezone.make_aware(timezone.datetime(2025, 12, 15, 14, 0)),
        )

    def test_event_update_form_get(self):
        """Testa exibição do formulário de edição (GET)."""
        url = reverse("scheduler:event_edit", args=[self.wedding.id, self.event.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("form", response.context)
        self.assertIn("event", response.context)
        self.assertEqual(response.context["event"], self.event)

    def test_event_update_post_valid(self):
        """Testa atualização com dados válidos (POST)."""
        url = reverse("scheduler:event_update", args=[self.wedding.id, self.event.id])

        data = {
            "title": "Evento Atualizado",
            "location": "Novo Local",
            "event_type": Event.TypeChoices.PAYMENT,
            "start_time_input": "15:00",
        }

        response = self.client.post(url, data)

        # Deve retornar 204 com trigger
        self.assertEqual(response.status_code, 204)

        # Verificar que evento foi atualizado
        self.event.refresh_from_db()
        self.assertEqual(self.event.title, "Evento Atualizado")
        self.assertEqual(self.event.location, "Novo Local")


class EventDeleteViewTest(SchedulerViewsTestCase):
    """Testes para EventDeleteView."""

    def setUp(self):
        """Configuração adicional."""
        super().setUp()

        self.event = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento a Deletar",
            start_time=timezone.now() + timedelta(days=7),
        )

    def test_event_delete_modal_view(self):
        """Testa exibição do modal de confirmação."""
        url = reverse(
            "scheduler:event_delete_modal",
            args=[self.wedding.id, self.event.id],
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "partials/confirm_delete_modal.html")
        self.assertIn("object_name", response.context)
        self.assertEqual(response.context["object_name"], "Evento a Deletar")

    def test_event_delete_post(self):
        """Testa deleção do evento (POST)."""
        url = reverse("scheduler:event_delete", args=[self.wedding.id, self.event.id])

        # Verificar que evento existe
        self.assertEqual(Event.objects.count(), 1)

        response = self.client.post(url)

        # Deve retornar JSON com trigger
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Verificar que evento foi deletado
        self.assertEqual(Event.objects.count(), 0)


class EventsJsonViewTest(SchedulerViewsTestCase):
    """Testes para EventsJsonView (API JSON)."""

    def setUp(self):
        """Configuração adicional."""
        super().setUp()

        # Criar eventos
        self.event1 = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento 1",
            start_time=timezone.now() + timedelta(days=7),
            end_time=timezone.now() + timedelta(days=7, hours=2),
        )

        self.event2 = Event.objects.create(
            wedding=self.wedding,
            planner=self.user,
            title="Evento 2",
            start_time=timezone.now() + timedelta(days=14),
        )

    def test_events_json_api(self):
        """Testa API JSON para FullCalendar."""
        url = reverse("scheduler:events_json")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")

        # Parsear JSON
        data = response.json()

        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["title"], "Evento 1")
        self.assertIn("start", data[0])
        self.assertIn("end", data[0])

    def test_events_json_api_filtered_by_wedding(self):
        """Testa filtro por wedding_id."""
        # Criar outro casamento e evento
        other_wedding = Wedding.objects.create(
            planner=self.user,
            groom_name="Pedro",
            bride_name="Ana",
            date=timezone.now().date() + timedelta(days=200),
            budget=40000.00,
        )

        Event.objects.create(
            wedding=other_wedding,
            planner=self.user,
            title="Evento Outro Wedding",
            start_time=timezone.now() + timedelta(days=21),
        )

        url = reverse("scheduler:events_json")
        response = self.client.get(url, {"wedding_id": self.wedding.id})

        data = response.json()

        # Deve retornar apenas eventos do wedding1
        self.assertEqual(len(data), 2)

    def test_events_json_api_unauthenticated(self):
        """Testa acesso sem autenticação."""
        self.client.logout()

        url = reverse("scheduler:events_json")
        response = self.client.get(url)

        # Deve redirecionar para login
        self.assertEqual(response.status_code, 302)
