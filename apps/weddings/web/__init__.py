"""
Interface Web do app weddings (Django + HTMX).

Re-exports para facilitar imports.
"""

from .forms import *
from .mixins import *
from .views import *

__all__ = [
    # Forms
    "WeddingForm",

    # Views
    "MyWeddingsView",
    "AddWeddingView",
    "EditWeddingView",
    "DeleteWeddingView",

    # Mixins
    "WeddingOwnershipMixin",
    "WeddingPaginationMixin",
]
