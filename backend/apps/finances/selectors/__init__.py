"""
Módulo de Selectors do domínio financeiro.
Exporta todos os seletores de leitura para orçamentos, categorias, despesas e parcelas.
"""

from .budget_category_selectors import (
    budget_category_get_selector,
    budget_category_list_selector,
)
from .budget_selectors import (
    budget_get_for_wedding_selector,
    budget_get_selector,
    budget_list_selector,
)
from .expense_selectors import (
    expense_get_selector,
    expense_list_selector,
)
from .installment_selectors import (
    installment_get_selector,
    installment_list_selector,
)


__all__ = [
    "budget_category_get_selector",
    "budget_category_list_selector",
    "budget_get_for_wedding_selector",
    "budget_get_selector",
    "budget_list_selector",
    "expense_get_selector",
    "expense_list_selector",
    "installment_get_selector",
    "installment_list_selector",
]
