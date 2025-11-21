"""
URLs da API de Users.
"""
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

# Router do DRF que gera automaticamente as URLs para o ViewSet
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = router.urls
