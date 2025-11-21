"""
Interface API REST do app weddings (Django REST Framework).

Re-exports para facilitar imports.
"""

from .serializers import *
from .views import *
from .permissions import *

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
