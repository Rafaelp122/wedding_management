from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.users.web.allauth_views import (
    CustomLoginView,
    CustomLogoutView,
    CustomPasswordResetView,
    CustomSignupView,
)

# Define as rotas principais do projeto.
urlpatterns = [
    # Painel administrativo padrão do Django
    path("admin/", admin.site.urls),
    # Página inicial e seções estáticas.
    path("", include("apps.pages.urls", namespace="pages")),
    # Views customizadas do allauth (com ícones e layout)
    path("accounts/signup/", CustomSignupView.as_view(), name="account_signup"),
    path("accounts/login/", CustomLoginView.as_view(), name="account_login"),
    path("accounts/logout/", CustomLogoutView.as_view(), name="account_logout"),
    path(
        "accounts/password/reset/",
        CustomPasswordResetView.as_view(),
        name="account_reset_password",
    ),
    # Demais rotas do allauth (password reset, email, etc)
    path("accounts/", include("allauth.urls")),
    # Rotas customizadas do usuário (edit profile, etc)
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
    path(
        "api/v1/",
        include(
            [
                path("", include("apps.users.api.urls")),
                path("weddings/", include("apps.weddings.api.urls")),
                path("items/", include("apps.items.api.urls")),
                path("scheduler/", include("apps.scheduler.api.urls")),
            ]
        ),
    ),
]

if settings.DEBUG:
    # Import debug toolbar only if available
    try:
        import debug_toolbar

        urlpatterns += [
            path("__debug__/", include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass  # Debug toolbar not installed

    # Adiciona a rota para servir arquivos de mídia (upload) localmente
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
