# config/urls.py
from django.conf import settings
from django.conf.urls.static import static
from django.urls import URLPattern, URLResolver, path

from config.api import api as ninja_api


urlpatterns: list[URLPattern | URLResolver] = [
    # Versão Ninja substituindo a DRF na mesma rota
    path("api/v1/", ninja_api.urls),
]

if getattr(settings, "ENABLE_DJANGO_ADMIN", False):
    from django.contrib import admin

    urlpatterns.insert(0, path("admin/", admin.site.urls))


# Servir arquivos de mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
