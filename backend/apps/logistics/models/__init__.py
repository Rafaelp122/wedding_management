"""
Models do domínio logístico.

Responsabilidade: Gestão de fornecedores, itens de logística e contratos.
Referências: RF07-RF13

Este módulo expõe os modelos principais:
- Supplier: Fornecedores de produtos e serviços (RF09)
- Contract: Contratos com fornecedores (RF10, RF13)
- Item: Itens de logística e serviços (RF07-RF08)
"""

from .contract import Contract
from .item import Item
from .supplier import Supplier


# Isso garante que o Django "veja" todos os modelos
__all__ = ["Supplier", "Contract", "Item"]
