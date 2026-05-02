"""
Configuração Local de Testes: App Logistics.

Este ficheiro regista as factories de logística. Permite validar fluxos
de contratação, conformidade de fornecedores e inventário do evento.
"""

import pytest
from pytest_factoryboy import register

from apps.weddings.tests.factories import WeddingFactory

from .factories import ContractFactory, ItemFactory, SupplierFactory


# Registo das factories logísticas
register(SupplierFactory)
register(ContractFactory)
register(ItemFactory)


@pytest.fixture
def active_contract(
    db, supplier_factory, wedding_factory, budget_category_factory, contract_factory
):
    """Fixture que devolve um contrato assinado e pronto para execução."""
    wedding = wedding_factory.create()
    supplier = supplier_factory.create(user_context=wedding.user_context)
    budget_cat = budget_category_factory.create(
        budget__wedding=wedding, wedding=wedding, company=wedding.company
    )
    return contract_factory.create(
        status="SIGNED",
        wedding=wedding,
        supplier=supplier,
        budget_category=budget_cat,
        description="Contrato de teste",
    )


@pytest.fixture
def supplier_with_items(db, supplier_factory, contract_factory, item_factory):
    """
    Fixture complexa que cria um fornecedor com um contrato e 3 itens.
    Garante que todos pertencem ao mesmo contexto de utilizador/casamento.
    """
    supplier = supplier_factory.create()

    # Criamos um casamento para este Planner (utilizador do fornecedor)
    wedding = WeddingFactory(user_context=supplier.user_context)

    # Criamos o contrato vinculado a este casamento e fornecedor
    contract = contract_factory.create(supplier=supplier, wedding=wedding)

    # Criamos os itens vinculados ao contrato
    items = item_factory.create_batch(3, contract=contract, wedding=wedding)

    return supplier, contract, items
