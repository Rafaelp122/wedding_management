from django.urls import path

from .views import ContractsPartialView

app_name = "contracts"

urlpatterns = [
    path(
        "partial/<int:wedding_id>/",
        ContractsPartialView.as_view(),
        name="partial_contracts"
    ),
]
