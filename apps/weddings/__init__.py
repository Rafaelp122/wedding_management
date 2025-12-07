"""
Weddings App - Interface Web (HTMX) + API (REST)

Este app gerencia casamentos com duas interfaces distintas:
- web/: Interface tradicional Django + HTMX
- api/: Interface RESTful com Django REST Framework

Este módulo usa imports lazy para evitar problemas de carregamento
circular e AppRegistryNotReady.
"""

from typing import TYPE_CHECKING

# Type checking imports (não executados em runtime)
if TYPE_CHECKING:
    from .api.permissions import IsWeddingOwner
    from .api.serializers import (
        WeddingDetailSerializer,
        WeddingListSerializer,
        WeddingSerializer,
    )
    from .api.views import WeddingViewSet
    from .models import Wedding
    from .querysets import WeddingQuerySet
    from .web.forms import WeddingForm
    from .web.mixins import (
        PlannerOwnershipMixin,
        WeddingFormLayoutMixin,
        WeddingHtmxListResponseMixin,
        WeddingListActionsMixin,
        WeddingModalContextMixin,
        WeddingPaginationContextMixin,
        WeddingQuerysetMixin,
    )
    from .web.views import (
        UpdateWeddingStatusView,
        WeddingCreateView,
        WeddingDeleteView,
        WeddingDetailView,
        WeddingListView,
        WeddingUpdateView,
    )

# Para manter compatibilidade, use imports lazy:
# from apps.weddings import Wedding
# from apps.weddings.web import WeddingForm
# from apps.weddings.api import WeddingSerializer


def __getattr__(name):
    """
    Lazy imports para evitar AppRegistryNotReady.

    Permite imports como:
    from apps.weddings import Wedding, WeddingForm, WeddingViewSet

    sem carregar os módulos até serem realmente necessários.
    """
    # Models e querysets (compartilhados)
    if name == "Wedding":
        from .models import Wedding

        return Wedding
    elif name == "WeddingQuerySet":
        from .querysets import WeddingQuerySet

        return WeddingQuerySet

    # Web - Forms
    elif name == "WeddingForm":
        from .web.forms import WeddingForm

        return WeddingForm

    # Web - Views
    elif name == "WeddingListView":
        from .web.views import WeddingListView

        return WeddingListView
    elif name == "WeddingCreateView":
        from .web.views import WeddingCreateView

        return WeddingCreateView
    elif name == "WeddingUpdateView":
        from .web.views import WeddingUpdateView

        return WeddingUpdateView
    elif name == "WeddingDeleteView":
        from .web.views import WeddingDeleteView

        return WeddingDeleteView
    elif name == "WeddingDetailView":
        from .web.views import WeddingDetailView

        return WeddingDetailView
    elif name == "UpdateWeddingStatusView":
        from .web.views import UpdateWeddingStatusView

        return UpdateWeddingStatusView

    # Web - Mixins
    elif name == "PlannerOwnershipMixin":
        from .web.mixins import PlannerOwnershipMixin

        return PlannerOwnershipMixin
    elif name == "WeddingModalContextMixin":
        from .web.mixins import WeddingModalContextMixin

        return WeddingModalContextMixin
    elif name == "WeddingFormLayoutMixin":
        from .web.mixins import WeddingFormLayoutMixin

        return WeddingFormLayoutMixin
    elif name == "WeddingQuerysetMixin":
        from .web.mixins import WeddingQuerysetMixin

        return WeddingQuerysetMixin
    elif name == "WeddingPaginationContextMixin":
        from .web.mixins import WeddingPaginationContextMixin

        return WeddingPaginationContextMixin
    elif name == "WeddingHtmxListResponseMixin":
        from .web.mixins import WeddingHtmxListResponseMixin

        return WeddingHtmxListResponseMixin
    elif name == "WeddingListActionsMixin":
        from .web.mixins import WeddingListActionsMixin

        return WeddingListActionsMixin

    # API - Serializers
    elif name == "WeddingSerializer":
        from .api.serializers import WeddingSerializer

        return WeddingSerializer
    elif name == "WeddingListSerializer":
        from .api.serializers import WeddingListSerializer

        return WeddingListSerializer
    elif name == "WeddingDetailSerializer":
        from .api.serializers import WeddingDetailSerializer

        return WeddingDetailSerializer

    # API - ViewSets
    elif name == "WeddingViewSet":
        from .api.views import WeddingViewSet

        return WeddingViewSet

    # API - Permissions
    elif name == "IsWeddingOwner":
        from .api.permissions import IsWeddingOwner

        return IsWeddingOwner

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    # Models
    "Wedding",
    "WeddingQuerySet",
    # Web - Forms
    "WeddingForm",
    # Web - Views
    "WeddingListView",
    "WeddingCreateView",
    "WeddingUpdateView",
    "WeddingDeleteView",
    "WeddingDetailView",
    "UpdateWeddingStatusView",
    # Web - Mixins
    "PlannerOwnershipMixin",
    "WeddingModalContextMixin",
    "WeddingFormLayoutMixin",
    "WeddingQuerysetMixin",
    "WeddingPaginationContextMixin",
    "WeddingHtmxListResponseMixin",
    "WeddingListActionsMixin",
    # API - Serializers
    "WeddingSerializer",
    "WeddingListSerializer",
    "WeddingDetailSerializer",
    # API - ViewSets
    "WeddingViewSet",
    # API - Permissions
    "IsWeddingOwner",
]
