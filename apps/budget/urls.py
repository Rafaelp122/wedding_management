# apps/budget/urls.py

from django.urls import path

from .views import BudgetPartialView

app_name = "budget"

urlpatterns = [
    path(
        "partial/<int:wedding_id>/",
        BudgetPartialView.as_view(),
        name="partial_budget"
    ),
]
