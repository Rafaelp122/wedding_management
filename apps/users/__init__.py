"""
App users - Sistema de autenticação e gerenciamento de usuários.

Este app implementa uma arquitetura híbrida:
- web/: Interface Django + HTMX (forms, views, urls)
- api/: REST API com Django REST Framework (serializers, views, urls)

Componentes compartilhados (na raiz do app):
- models.py: CustomUser model
- admin.py: Configuração do Django Admin
"""


# Lazy imports para evitar AppRegistryNotReady durante a inicialização
def __getattr__(name):
    """
    Implementa lazy imports para compatibilidade com código legado.
    
    Permite imports como:
    - from apps.users import forms
    - from apps.users import views
    
    Que serão redirecionados para:
    - from apps.users.web import forms
    - from apps.users.web import views
    """
    # Mapeamento de módulos web (interface Django + HTMX)
    web_modules = {
        'forms': 'apps.users.web.forms',
        'views': 'apps.users.web.views',
        'urls': 'apps.users.web.urls',
    }
    
    # Mapeamento de módulos API (REST Framework)
    api_modules = {
        'serializers': 'apps.users.api.serializers',
        'api': 'apps.users.api',
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
