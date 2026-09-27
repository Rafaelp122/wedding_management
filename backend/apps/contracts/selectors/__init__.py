"""Seletores do domínio de Contratos e Termos Aditivos."""

from apps.contracts.selectors.contract_selectors import (
    contract_addendum_get_selector,
    contract_addendum_list_selector,
    contract_consolidated_total_selector,
    contract_detail_aggregate_selector,
    contract_get_selector,
    contract_list_selector,
    contract_pending_count_selector,
)
from apps.suppliers.selectors import (
    supplier_get_selector,
    supplier_list_selector,
)


__all__ = [
    "contract_addendum_get_selector",
    "contract_addendum_list_selector",
    "contract_consolidated_total_selector",
    "contract_detail_aggregate_selector",
    "contract_get_selector",
    "contract_list_selector",
    "contract_pending_count_selector",
    "supplier_get_selector",
    "supplier_list_selector",
]
