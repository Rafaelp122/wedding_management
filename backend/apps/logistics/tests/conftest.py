"""
Configuração Local de Testes: App Logistics.

Este ficheiro regista as factories de logística. Permite validar fluxos
de contratação, conformidade de fornecedores e inventário do evento.
"""

import pytest
from pytest_factoryboy import register

from apps.weddings.tests.model_factories import WeddingFactory

from .model_factories import ContractFactory, ItemFactory, SupplierFactory


# Registo das factories logísticas
register(SupplierFactory)
register(ContractFactory)
register(ItemFactory)


@pytest.fixture
def active_contract(db, contract_factory):
    """Fixture que devolve um contrato assinado e pronto para execução."""
    return contract_factory.create(status="SIGNED")


@pytest.fixture
def supplier_with_items(db, supplier_factory, contract_factory, item_factory):
    """
    Fixture complexa que cria um fornecedor com um contrato e 3 itens.
    Garante que todos pertencem ao mesmo contexto de utilizador/casamento.
    """
    supplier = supplier_factory.create()

    # Criamos um casamento para este Planner (utilizador do fornecedor)
    wedding = WeddingFactory(planner=supplier.user)

    # Criamos o contrato vinculado a este casamento e fornecedor
    contract = contract_factory.create(supplier=supplier, wedding=wedding)

    # Criamos os itens vinculados ao contrato
    items = item_factory.create_batch(3, contract=contract, wedding=wedding)

    return supplier, contract, items
