"""
Models do domínio financeiro.

Responsabilidade: Gestão de orçamentos, categorias, despesas e parcelamentos.
Referências: RF03-RF05

Este módulo expõe os modelos principais:
- Budget: Orçamento mestre do casamento (RF03)
- BudgetCategory: Categorias de gastos (RF03)
- Expense: Despesas vinculadas a categorias e contratos (RF04, RF05)
- Installment: Parcelamentos de despesas (RF04)
"""

# apps/finances/models/__init__.py
from .budget import Budget
from .category import BudgetCategory
from .expense import Expense
from .installment import Installment


__all__ = ["Budget", "BudgetCategory", "Expense", "Installment"]
