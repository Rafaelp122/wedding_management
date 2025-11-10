from django.urls import path
from .views import ContractsPartialView


# Define o namespace para o app de contratos
app_name = "contracts"

# Rotas do app de contratos
urlpatterns = [
    # Exibe a lista parcial de contratos de um casamento específico
    path(
        "partial/<int:wedding_id>/",
        ContractsPartialView.as_view(),
        name="partial_contracts"
    ),
]
