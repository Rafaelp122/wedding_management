"""
Interface API REST do app weddings (Django REST Framework).

Re-exports para facilitar imports.
"""

from .permissions import *
from .serializers import *
from .views import *

__all__ = [
    # Serializers
    "WeddingSerializer",
    "WeddingListSerializer",
    "WeddingDetailSerializer",

    # ViewSets
    "WeddingViewSet",

    # Permissions
    "IsWeddingOwner",
]
