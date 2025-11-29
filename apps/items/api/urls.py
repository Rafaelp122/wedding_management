"""
URLs da API REST de Item.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ItemViewSet

# Configuração do Router DRF
router = DefaultRouter()
router.register(r"items", ItemViewSet, basename="item")

app_name = "items_api"

urlpatterns = [
    path("", include(router.urls)),
]
