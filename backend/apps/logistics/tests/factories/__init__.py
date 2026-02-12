from .dto_factories import ContractDTOFactory, ItemDTOFactory, SupplierDTOFactory
from .model_factories import ContractFactory, ItemFactory, SupplierFactory


# Isso garante que o Django "veja" todos os modelos
__all__ = [
    "SupplierDTOFactory",
    "ContractDTOFactory",
    "ItemDTOFactory",
    "SupplierFactory",
    "ContractFactory",
    "ItemFactory",
]
