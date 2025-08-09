from django.test import TestCase
from django.urls import resolve, reverse

from apps.pages import views


class TestPagesViews(TestCase):
    def test_pages_home_view_is_correct(self):
        view = resolve(
            reverse("pages:home")
        )
        self.assertIs(view.func, views.home)

    def test_pages_home_view_returns_status_code_200_OK(self):
        response = self.client.get(reverse("pages:home"))
        self.assertEqual(response.status_code, 200)

    def test_pages_home_template_is_correct(self):
        response = self.client.get(reverse("pages:home"))
        self.assertTemplateUsed(response, "pages/home.html")

    def test_pages_home_contains_expected_content(self):
        response = self.client.get(reverse("pages:home"))
        self.assertContains(response, "Gestão de Casamentos")

    def test_pages_contact_us_view_is_correct(self):
        view = resolve(
            reverse("pages:contact_us")
        )
        self.assertIs(view.func, views.contact_us)

    def test_pages_contact_us_view_returns_status_code_200_OK(self):
        response = self.client.get(reverse("pages:contact_us"))
        self.assertEqual(response.status_code, 200)

    def test_pages_contact_us_template_is_correct(self):
        response = self.client.get(reverse("pages:contact_us"))
        self.assertTemplateUsed(response, "pages/contact-us.html")

    def test_pages_contact_us_contains_expected_content(self):
        response = self.client.get(reverse("pages:contact_us"))
        self.assertContains(response, "Fale Conosco")
