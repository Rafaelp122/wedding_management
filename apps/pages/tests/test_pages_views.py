from django.test import TestCase
from django.urls import resolve, reverse

from apps.pages import views


class TestPagesViews(TestCase):
    def test_pages_home_view_is_correct(self):
        view = resolve(
            reverse("pages:home")
        )
        self.assertIs(view.func, views.home)
