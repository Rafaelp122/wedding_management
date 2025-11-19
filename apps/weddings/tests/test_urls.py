from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.weddings.views import (
    UpdateWeddingStatusView,
    WeddingCreateView,
    WeddingDeleteView,
    WeddingDetailView,
    WeddingListView,
    WeddingUpdateView,
)


class WeddingUrlsTest(SimpleTestCase):
    """
    Testa se as URLs (paths) estão resolvendo para as Views corretas.
    Garante que mudanças acidentais nas rotas sejam detectadas.
    """

    def test_list_url_resolves(self):
        url = reverse("weddings:my_weddings")
        self.assertEqual(resolve(url).func.view_class, WeddingListView)

    def test_detail_url_resolves(self):
        url = reverse("weddings:wedding_detail", kwargs={"wedding_id": 1})
        self.assertEqual(resolve(url).func.view_class, WeddingDetailView)

    def test_create_url_resolves(self):
        url = reverse("weddings:create_wedding")
        self.assertEqual(resolve(url).func.view_class, WeddingCreateView)

    def test_update_url_resolves(self):
        url = reverse("weddings:edit_wedding", kwargs={"id": 1})
        self.assertEqual(resolve(url).func.view_class, WeddingUpdateView)

    def test_delete_url_resolves(self):
        url = reverse("weddings:delete_wedding", kwargs={"id": 1})
        self.assertEqual(resolve(url).func.view_class, WeddingDeleteView)

    def test_update_status_url_resolves(self):
        url = reverse("weddings:update_wedding_status", kwargs={"id": 1})
        self.assertEqual(resolve(url).func.view_class, UpdateWeddingStatusView)
