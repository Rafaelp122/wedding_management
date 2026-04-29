"""
Configuração Local de Testes: App Logistics.

Este ficheiro regista as factories de logística. Permite validar fluxos
de contratação, conformidade de fornecedores e inventário do evento.
"""

import pytest
from pytest_factoryboy import register

from apps.events.tests.factories import EventFactory

from .factories import ContractFactory, ItemFactory, SupplierFactory


# Registo das factories logísticas
register(SupplierFactory)
register(ContractFactory)
register(ItemFactory)


@pytest.fixture
def active_contract(
    db, supplier_factory, event_factory, budget_category_factory, contract_factory
):
    """Fixture que devolve um contrato assinado e pronto para execução."""
    event = event_factory.create()
    supplier = supplier_factory.create(company=event.company)
    budget_cat = budget_category_factory.create(budget__event=event, event=event)
    return contract_factory.create(
        status="SIGNED",
        event=event,
        supplier=supplier,
        budget_category=budget_cat,
        description="Contrato de teste",
    )


@pytest.fixture
def supplier_with_items(db, supplier_factory, contract_factory, item_factory):
    """
    Fixture complexa que cria um fornecedor com um contrato e 3 itens.
    Garante que todos pertencem ao mesmo contexto de utilizador/evento.
    """
    supplier = supplier_factory.create()

    # Criamos um evento para este Company (empresa do fornecedor)
    event = EventFactory(company=supplier.company)

    # Criamos o contrato vinculado a este evento e fornecedor
    contract = contract_factory.create(supplier=supplier, event=event)

    # Criamos os itens vinculados ao contrato
    items = item_factory.create_batch(3, contract=contract, event=event)

    return supplier, contract, items
