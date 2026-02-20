from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EventsViewSet


# Configuração do router para o módulo de agendamento
# O DefaultRouter gera automaticamente os padrões de URL para as ações padrão do ViewSet
router = DefaultRouter()
router.register(r"events", EventsViewSet, basename="event")

app_name = "scheduler"

urlpatterns = [
    # Inclui as rotas geradas pelo router
    path("", include(router.urls)),
]
