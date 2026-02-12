from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ContractViewSet, ItemViewSet, SupplierViewSet


# O DefaultRouter gerencia automaticamente as barras e os IDs/UUIDs
router = DefaultRouter()
router.register(r"suppliers", SupplierViewSet, basename="supplier")
router.register(r"contracts", ContractViewSet, basename="contract")
router.register(r"items", ItemViewSet, basename="item")

urlpatterns = [
    path("", include(router.urls)),
]
