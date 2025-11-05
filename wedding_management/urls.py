from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.pages.urls", namespace="pages")),
    path("usuario/", include(("apps.users.urls", "users"), namespace="users")),
    path(
        "casamentos/", include(("apps.weddings.urls", "weddings"), namespace="weddings")
    ),
    path("orcamento/", include(("apps.budget.urls", "budget"), namespace="budget")),
    path(
        "contratos/",
        include(("apps.contracts.urls", "contracts"), namespace="contracts"),
    ),
    path("itens/", include(("apps.items.urls", "items"), namespace="items")),
    path(
        "scheduler/",
        include(("apps.scheduler.urls", "scheduler"), namespace="scheduler"),
    ),
]
