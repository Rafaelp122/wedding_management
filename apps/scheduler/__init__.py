"""
App scheduler - Sistema de agendamento de eventos para casamentos.

Este app implementa uma arquitetura híbrida:
- web/: Interface Django + HTMX (forms, views, mixins, urls)
- api/: REST API com Django REST Framework (serializers, views, permissions, urls)

Componentes compartilhados (na raiz do app):
- models.py: Modelos de dados
- querysets.py: QuerySets customizados
- admin.py: Configuração do Django Admin
- constants.py: Constantes compartilhadas
"""

# Lazy imports para evitar AppRegistryNotReady durante a inicialização
def __getattr__(name):
    """
    Implementa lazy imports para compatibilidade com código legado.
    
    Permite imports como:
    - from apps.scheduler import forms
    - from apps.scheduler import views
    - from apps.scheduler import mixins
    
    Que serão redirecionados para:
    - from apps.scheduler.web import forms
    - from apps.scheduler.web import views
    - from apps.scheduler.web import mixins
    """
    # Mapeamento de módulos web (interface Django + HTMX)
    web_modules = {
        'forms': 'apps.scheduler.web.forms',
        'views': 'apps.scheduler.web.views',
        'mixins': 'apps.scheduler.web.mixins',
        'urls': 'apps.scheduler.web.urls',
        'api_views': 'apps.scheduler.web.api_views',
    }

    # Mapeamento de módulos API (REST Framework)
    api_modules = {
        'serializers': 'apps.scheduler.api.serializers',
        'api': 'apps.scheduler.api',
    }

    # Verifica se é um módulo web
    if name in web_modules:
        import importlib
        return importlib.import_module(web_modules[name])

    # Verifica se é um módulo API
    if name in api_modules:
        import importlib
        return importlib.import_module(api_modules[name])

    # Se não encontrar, lança AttributeError padrão
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
