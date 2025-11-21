from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

# Define as rotas principais do projeto.
urlpatterns = [
    # Painel administrativo padrão do Django
    path("admin/", admin.site.urls),
    # Página inicial e seções estáticas.
    path("", include("apps.pages.urls", namespace="pages")),
    # Rotas relacionadas a autenticação e perfis de usuário
    path("usuario/", include(("apps.users.urls", "users"), namespace="users")),
    # Área de casamentos (listagem, detalhes, gerenciamento)
    path(
        "casamentos/", include(("apps.weddings.urls", "weddings"), namespace="weddings")
    ),
    # Orçamentos de casamento
    path("orcamento/", include(("apps.budget.urls", "budget"), namespace="budget")),
    # Contratos entre clientes, fornecedores e cerimonialistas
    path(
        "contratos/",
        include(("apps.contracts.urls", "contracts"), namespace="contracts"),
    ),
    # Itens e serviços relacionados a casamentos
    path("itens/", include(("apps.items.urls", "items"), namespace="items")),
    # Agendamentos e tarefas do planejador de casamentos
    path(
        "scheduler/",
        include(("apps.scheduler.urls", "scheduler"), namespace="scheduler"),
    ),
]

if settings.DEBUG:
    # Importe a toolbar dentro do if
    import debug_toolbar

    # Adiciona as URLs do debug toolbar
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    
    # Adiciona a rota para servir arquivos de mídia (upload) localmente
    # ISSO AQUI QUE ESTAVA QUEBRADO E IMPEDIA O DOWNLOAD
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)