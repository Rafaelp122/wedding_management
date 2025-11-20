from django.test import SimpleTestCase
from django.urls import resolve, reverse

from apps.budget.views import BudgetPartialView


class BudgetUrlsTest(SimpleTestCase):
    def test_partial_budget_url_resolves(self):
        url = reverse("budget:partial_budget", kwargs={"wedding_id": 1})
        self.assertEqual(resolve(url).func.view_class, BudgetPartialView)
