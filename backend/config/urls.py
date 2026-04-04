# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import URLPattern, URLResolver, path

from config.api import api as ninja_api


urlpatterns: list[URLPattern | URLResolver] = [
    path("admin/", admin.site.urls),
    # Versão Ninja substituindo a DRF na mesma rota
    path("api/v1/", ninja_api.urls),
]

# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
