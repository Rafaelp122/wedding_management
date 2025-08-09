from django.test import TestCase
from django.urls import reverse


class TestPagesUrls(TestCase):
    """Teste para verificar se as urls estão corretas"""
    def test_pages_home_url_is_correct(self):
        url = reverse("pages:home")
        self.assertEqual(url, "/")

    def test_pages_contact_us_url_is_correct(self):
        url = reverse("pages:contact_us")
        self.assertEqual(url, "/fale-conosco/")
