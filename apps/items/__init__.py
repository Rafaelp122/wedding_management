"""
Items App - Interface Web (HTMX) + API (REST)

Este app gerencia itens de orçamento com duas interfaces distintas:
- web/: Interface tradicional Django + HTMX
- api/: Interface RESTful com Django REST Framework

Este módulo usa imports lazy para evitar problemas de carregamento
circular e AppRegistryNotReady.
"""


def __getattr__(name):
    """
    Lazy imports para evitar AppRegistryNotReady.
    
    Permite imports como:
    from apps.items import Item, ItemForm, ItemViewSet
    
    sem carregar os módulos até serem realmente necessários.
    """
    # Models e querysets (compartilhados)
    if name == "Item":
        from .models import Item
        return Item
    elif name == "ItemQuerySet":
        from .querysets import ItemQuerySet
        return ItemQuerySet

    # Web - Forms
    elif name == "ItemForm":
        from .web.forms import ItemForm
        return ItemForm

    # Web - Views
    elif name == "ItemListView":
        from .web.views import ItemListView
        return ItemListView
    elif name == "AddItemView":
        from .web.views import AddItemView
        return AddItemView
    elif name == "EditItemView":
        from .web.views import EditItemView
        return EditItemView
    elif name == "DeleteItemView":
        from .web.views import DeleteItemView
        return DeleteItemView
    elif name == "UpdateItemStatusView":
        from .web.views import UpdateItemStatusView
        return UpdateItemStatusView

    # Web - Mixins
    elif name == "ItemWeddingContextMixin":
        from .web.mixins import ItemWeddingContextMixin
        return ItemWeddingContextMixin
    elif name == "ItemQuerysetMixin":
        from .web.mixins import ItemQuerysetMixin
        return ItemQuerysetMixin
    elif name == "ItemListActionsMixin":
        from .web.mixins import ItemListActionsMixin
        return ItemListActionsMixin

    # API - Serializers
    elif name == "ItemSerializer":
        from .api.serializers import ItemSerializer
        return ItemSerializer
    elif name == "ItemListSerializer":
        from .api.serializers import ItemListSerializer
        return ItemListSerializer
    elif name == "ItemDetailSerializer":
        from .api.serializers import ItemDetailSerializer
        return ItemDetailSerializer

    # API - ViewSets
    elif name == "ItemViewSet":
        from .api.views import ItemViewSet
        return ItemViewSet

    # API - Permissions
    elif name == "IsItemOwner":
        from .api.permissions import IsItemOwner
        return IsItemOwner

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Models
    "Item",
    "ItemQuerySet",
    # Web - Forms
    "ItemForm",
    # Web - Views
    "ItemListView",
    "AddItemView",
    "EditItemView",
    "DeleteItemView",
    "UpdateItemStatusView",
    # Web - Mixins
    "ItemWeddingContextMixin",
    "ItemQuerysetMixin",
    "ItemListActionsMixin",
    # API - Serializers
    "ItemSerializer",
    "ItemListSerializer",
    "ItemDetailSerializer",
    # API - ViewSets
    "ItemViewSet",
    # API - Permissions
    "IsItemOwner",
]
