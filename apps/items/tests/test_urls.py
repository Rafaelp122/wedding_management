from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.items import views


class ItemUrlsTest(SimpleTestCase):
    def test_partial_items_url_resolves(self):
        url = reverse("items:partial_items", kwargs={"wedding_id": 1})
        self.assertEqual(resolve(url).func.view_class, views.ItemListView)

    def test_add_item_url_resolves(self):
        url = reverse("items:add_item", kwargs={"wedding_id": 1})
        self.assertEqual(resolve(url).func.view_class, views.AddItemView)

    def test_edit_item_url_resolves(self):
        url = reverse("items:edit_item", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, views.EditItemView)

    def test_delete_item_url_resolves(self):
        url = reverse("items:delete_item", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, views.ItemDeleteView)

    def test_update_status_url_resolves(self):
        url = reverse("items:update_status", kwargs={"pk": 1})
        self.assertEqual(resolve(url).func.view_class, views.UpdateItemStatusView)
