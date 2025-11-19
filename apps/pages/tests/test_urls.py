from django.test import SimpleTestCase
from django.urls import reverse, resolve
from apps.pages import views


class PagesUrlsTest(SimpleTestCase):
    def test_home_url_resolves(self):
        url = reverse("pages:home")
        self.assertEqual(resolve(url).func.view_class, views.HomeView)

    def test_contact_submit_url_resolves(self):
        url = reverse("pages:contact_submit")
        self.assertEqual(resolve(url).func.view_class, views.ContactFormSubmitView)
