from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Define as rotas principais do projeto.
urlpatterns = [
    # Painel administrativo padrão do Django
    path("admin/", admin.site.urls),
    # --- API REST (DRF) ---
    # API v1 - Backend completo
    path(
        "api/v1/",
        include(
            [
                # Authentication
                path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain"),
                path(
                    "auth/token/refresh/",
                    TokenRefreshView.as_view(),
                    name="token_refresh",
                ),
                # Apps APIs will be created here
            ]
        ),
    ),
    # --- API Documentation (RNF06) ---
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

# Adiciona a rota para servir arquivos de mídia (upload) localmente em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
