"""
URLs da API REST de Wedding.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import WeddingViewSet

# Configuração do Router DRF
router = DefaultRouter()
router.register(r"weddings", WeddingViewSet, basename="wedding")

app_name = "weddings_api"

urlpatterns = [
    path("", include(router.urls)),
]
