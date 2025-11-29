"""
URLs da API de Events (Scheduler).
"""

from rest_framework.routers import DefaultRouter

from .views import EventViewSet

# Router do DRF que gera automaticamente as URLs para o ViewSet
router = DefaultRouter()
router.register(r"events", EventViewSet, basename="event")

urlpatterns = router.urls
