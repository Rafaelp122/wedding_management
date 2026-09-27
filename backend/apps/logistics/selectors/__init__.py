"""
Módulo de Selectors do domínio logístico.
Exporta todos os seletores de leitura para fornecedores, contratos e itens.
"""

from .item_selectors import (
    item_get_selector,
    item_list_selector,
)


__all__ = [
    "item_get_selector",
    "item_list_selector",
]
