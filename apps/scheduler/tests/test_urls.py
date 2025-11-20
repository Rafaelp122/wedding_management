"""
Testes para as URLs do app scheduler.
"""
from django.test import TestCase
from django.urls import resolve, reverse

from apps.scheduler import api_views, views


class SchedulerUrlsTest(TestCase):
    """Testes para as URLs do scheduler."""

    def test_partial_scheduler_url(self):
        """Testa URL do calendário parcial."""
        url = reverse("scheduler:partial_scheduler", args=[1])
        self.assertEqual(url, "/scheduler/partial/1/")

        # Verificar resolve
        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.SchedulerPartialView)

    def test_event_new_url(self):
        """Testa URL de novo evento (formulário GET)."""
        url = reverse("scheduler:event_new", args=[1])
        self.assertEqual(url, "/scheduler/partial/1/event/new/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventCreateView)

    def test_event_create_url(self):
        """Testa URL de criação de evento (POST)."""
        url = reverse("scheduler:event_create", args=[1])
        self.assertEqual(url, "/scheduler/partial/1/event/create/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventCreateView)

    def test_event_detail_url(self):
        """Testa URL de detalhes do evento."""
        url = reverse("scheduler:event_detail", args=[1, 5])
        self.assertEqual(url, "/scheduler/partial/1/event/5/detail/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventDetailView)

    def test_event_edit_url(self):
        """Testa URL de edição de evento (formulário GET)."""
        url = reverse("scheduler:event_edit", args=[1, 5])
        self.assertEqual(url, "/scheduler/partial/1/event/5/edit/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventUpdateView)

    def test_event_update_url(self):
        """Testa URL de atualização de evento (POST)."""
        url = reverse("scheduler:event_update", args=[1, 5])
        self.assertEqual(url, "/scheduler/partial/1/event/5/update/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventUpdateView)

    def test_event_delete_modal_url(self):
        """Testa URL do modal de confirmação de deleção."""
        url = reverse("scheduler:event_delete_modal", args=[1, 5])
        self.assertEqual(url, "/scheduler/partial/1/event/5/delete/modal/")

        resolved = resolve(url)
        self.assertEqual(
            resolved.func.view_class, views.EventDeleteModalView
        )

    def test_event_delete_url(self):
        """Testa URL de deleção de evento (POST)."""
        url = reverse("scheduler:event_delete", args=[1, 5])
        self.assertEqual(url, "/scheduler/partial/1/event/5/delete/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, views.EventDeleteView)

    def test_events_json_url(self):
        """Testa URL da API JSON."""
        url = reverse("scheduler:events_json")
        self.assertEqual(url, "/scheduler/api/events/")

        resolved = resolve(url)
        self.assertEqual(resolved.func.view_class, api_views.EventsJsonView)

    def test_url_namespaces(self):
        """Testa que todas as URLs usam o namespace 'scheduler'."""
        urls = [
            "partial_scheduler",
            "event_new",
            "event_create",
            "event_detail",
            "event_edit",
            "event_update",
            "event_delete_modal",
            "event_delete",
            "events_json",
        ]

        for url_name in urls:
            try:
                reverse(f"scheduler:{url_name}", args=[1] * 2)
            except Exception:
                try:
                    reverse(f"scheduler:{url_name}", args=[1])
                except Exception:
                    try:
                        reverse(f"scheduler:{url_name}")
                    except Exception as e:
                        self.fail(
                            f"URL 'scheduler:{url_name}' não encontrada: {e}"
                        )
