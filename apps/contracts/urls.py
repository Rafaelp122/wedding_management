from django.urls import path
from . import views

app_name = "contracts"

urlpatterns = [
    path(
        "partial/<int:wedding_id>/", views.partial_contracts, name="partial_contracts"
    ),
]
