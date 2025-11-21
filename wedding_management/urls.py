from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# Define as rotas principais do projeto.
# Cada app tem seu próprio arquivo de rotas, que é incluído aqui.

urlpatterns = [
    # Painel administrativo padrão do Django
    path("admin/", admin.site.urls),
    # Página inicial e seções estáticas.
    path("", include("apps.pages.urls", namespace="pages")),
    # Rotas relacionadas a autenticação e perfis de usuário - Interface Web
    path(
        "usuario/",
        include(("apps.users.web.urls", "users"), namespace="users"),
    ),
    # Área de casamentos (listagem, detalhes, gerenciamento) - Interface Web
    path(
        "casamentos/",
        include(("apps.weddings.web.urls", "weddings"), namespace="weddings"),
    ),
    # Orçamentos de casamento
    path("orcamento/", include(("apps.budget.urls", "budget"), namespace="budget")),
    # Contratos entre clientes, fornecedores e cerimonialistas
    path(
        "contratos/",
        include(("apps.contracts.urls", "contracts"), namespace="contracts"),
    ),
    # Itens e serviços relacionados a casamentos - Interface Web
    path("itens/", include(("apps.items.web.urls", "items"), namespace="items")),
    # Agendamentos e tarefas do planejador de casamentos - Interface Web
    path(
        "scheduler/",
        include(("apps.scheduler.web.urls", "scheduler"), namespace="scheduler"),
    ),
    # --- API REST (DRF) ---
    # API v1 para integrações externas (mobile, calendários, webhooks)
    path("api/v1/", include([
        path("", include("apps.users.api.urls")),
        path("weddings/", include("apps.weddings.api.urls")),
        path("items/", include("apps.items.api.urls")),
        path("scheduler/", include("apps.scheduler.api.urls")),
    ])),
]

if settings.DEBUG:
    # 3. Importe a toolbar dentro do if
    import debug_toolbar

    urlpatterns = [
        # 4. Adicione a URL da toolbar
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
