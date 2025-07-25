# apps/budget/urls.py

from django.urls import path
from . import views

app_name = "budget"

urlpatterns = [
    path("<int:id>/", views.budget_detail, name="budget_detail"),
]
