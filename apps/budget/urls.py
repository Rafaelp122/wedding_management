# apps/budget/urls.py
from django.urls import path
from .views import BudgetPartialView

# Define o namespace para o app de orçamentos
app_name = "budget"

# Rotas relacionadas a orçamentos de casamento
urlpatterns = [
    # Exibe ou atualiza parcialmente o orçamento de um casamento específico
    # O parâmetro <int:wedding_id> identifica qual casamento está sendo tratado
    path(
        "partial/<int:wedding_id>/",
        BudgetPartialView.as_view(),
        name="partial_budget"
    ),
]
