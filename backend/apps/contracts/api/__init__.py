"""API de Contratos e Termos Aditivos."""

from apps.contracts.api.contracts import contracts_router
from apps.suppliers.api import suppliers_router


__all__ = ["contracts_router", "suppliers_router"]
