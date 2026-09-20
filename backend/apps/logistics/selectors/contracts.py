"""
Módulo de seletores para Contratos de Logística.
Permite import direto via apps.logistics.selectors.contracts.
"""

from apps.logistics.selectors.contract_selectors import (
    contract_consolidated_total_selector,
    contract_detail_aggregate_selector,
    contract_get_selector,
    contract_list_selector,
    contract_pending_count_selector,
)


__all__ = [
    "contract_consolidated_total_selector",
    "contract_detail_aggregate_selector",
    "contract_get_selector",
    "contract_list_selector",
    "contract_pending_count_selector",
]
