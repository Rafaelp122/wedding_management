"""
Módulo de Selectors do domínio logístico.
Exporta todos os seletores de leitura para fornecedores, contratos e itens.
"""

from .contract_selectors import (
    contract_get_selector,
    contract_list_selector,
    contract_pending_count_selector,
)
from .item_selectors import (
    item_get_selector,
    item_list_selector,
)
from .supplier_selectors import (
    supplier_get_selector,
    supplier_list_selector,
)


__all__ = [
    "contract_get_selector",
    "contract_list_selector",
    "contract_pending_count_selector",
    "item_get_selector",
    "item_list_selector",
    "supplier_get_selector",
    "supplier_list_selector",
]
