# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


# Agrupamento das rotas da API v1 para clareza
api_v1_patterns = [
    path("auth/", include("apps.users.urls")),
    path("weddings/", include("apps.weddings.urls")),
    path("logistics/", include("apps.logistics.urls")),
    path("finances/", include("apps.finances.urls")),
    path("scheduler/", include("apps.scheduler.urls")),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]

urlpatterns = [
    path("admin/", admin.site.urls),
    # Versão 1 da API
    path("api/v1/", include((api_v1_patterns, "api"), namespace="v1")),
    # Documentação (RNF06)
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="v1:schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/", SpectacularRedocView.as_view(url_name="v1:schema"), name="redoc"
    ),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
