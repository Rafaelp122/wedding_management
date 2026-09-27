"""
Testes unitários e de integração para Custom QuerySets e Selectors do app logistics.
Valida isolamento multi-tenant, encadeamento de métodos, filtros e buscas de itens.
"""

from __future__ import annotations

from typing import Any, cast
from uuid import uuid4

import pytest

from apps.contracts.tests.factories import ContractFactory as _ContractFactory
from apps.core.exceptions import ObjectNotFoundError
from apps.logistics.models import SupplyItem
from apps.logistics.selectors import (
    item_get_selector,
    item_list_selector,
)
from apps.logistics.tests.factories import (
    ItemFactory as _ItemFactory,
)
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def ContractFactory(*args: Any, **kwargs: Any) -> Any:
    return _ContractFactory(*args, **kwargs)


def ItemFactory(*args: Any, **kwargs: Any) -> SupplyItem:
    return cast(SupplyItem, _ItemFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


# ==============================================================================
# TESTES DE CUSTOM QUERYSET DE ITENS (ItemQuerySet)
# ==============================================================================


@pytest.mark.django_db
class TestItemQuerySet:
    """Testes para os métodos encadeáveis de ItemQuerySet (SupplyItem)."""

    def test_for_wedding_filter(self, user: User) -> None:
        """for_wedding filtra itens de um casamento específico."""
        wedding_a = WeddingFactory(user_context=user)
        wedding_b = WeddingFactory(user_context=user)
        item_a = ItemFactory(wedding=wedding_a, company=user.company)
        ItemFactory(wedding=wedding_b, company=user.company)

        qs = SupplyItem.objects.for_tenant(user.company).for_wedding(wedding_a)
        assert qs.count() == 1
        assert qs.first() == item_a

    def test_for_contract_filter(self, user: User) -> None:
        """for_contract filtra itens associados a um contrato."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)
        item_c = ItemFactory(wedding=wedding, contract=contract, company=user.company)
        ItemFactory(wedding=wedding, contract=None, company=user.company)

        qs = SupplyItem.objects.for_tenant(user.company).for_contract(contract)
        assert qs.count() == 1
        assert qs.first() == item_c

    def test_search_filter(self, user: User) -> None:
        """search filtra itens por nome."""
        wedding = WeddingFactory(user_context=user)
        ItemFactory(
            wedding=wedding,
            company=user.company,
            name="Taças de Cristal",
        )
        ItemFactory(
            wedding=wedding,
            company=user.company,
            name="Guardanapos",
        )

        qs = SupplyItem.objects.for_tenant(user.company).search("Cristal")
        assert qs.count() == 1
        item = qs.first()
        assert item is not None
        assert item.name == "Taças de Cristal"


# ==============================================================================
# TESTES DE SELECTORS DE ITENS (item_get_selector, item_list_selector)
# ==============================================================================


@pytest.mark.django_db
class TestItemSelectors:
    """Testes para os seletores de leitura de itens de suprimentos."""

    def test_item_list_selector_multitenancy(self) -> None:
        """item_list_selector respeita isolamento multitenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)
        ItemFactory(wedding=wedding_a, company=user_a.company, name="Item A")
        ItemFactory(wedding=wedding_b, company=user_b.company, name="Item B")

        qs_a = item_list_selector(user_a.company)
        assert qs_a.count() == 1
        item_a = qs_a.first()
        assert item_a is not None and item_a.name == "Item A"

        qs_b = item_list_selector(user_b.company)
        assert qs_b.count() == 1
        item_b = qs_b.first()
        assert item_b is not None and item_b.name == "Item B"

    def test_item_list_selector_filters(self, user: User) -> None:
        """item_list_selector filtra por casamento, busca e contrato."""
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)
        ItemFactory(
            wedding=wedding,
            contract=contract,
            company=user.company,
            name="Taças de Cristal",
        )
        ItemFactory(
            wedding=wedding,
            contract=None,
            company=user.company,
            name="Pratos Rasos",
        )

        assert item_list_selector(user.company, wedding_id=wedding.uuid).count() == 2
        assert item_list_selector(user.company, search="Taças").count() == 1
        assert item_list_selector(user.company, contract_id=contract.uuid).count() == 1

    def test_item_get_selector_success(self, user: User) -> None:
        """item_get_selector recupera item corretamente."""
        wedding = WeddingFactory(user_context=user)
        item = ItemFactory(
            wedding=wedding, company=user.company, name="Microfone sem Fio"
        )

        res = item_get_selector(user.company, item.uuid)
        assert res.uuid == item.uuid
        assert res.name == "Microfone sem Fio"

    def test_item_get_selector_not_found_and_multitenancy(self) -> None:
        """item_get_selector valida inexistência e isolamento."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        item_b = ItemFactory(wedding=wedding_b, company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            item_get_selector(user_a.company, uuid4())

        with pytest.raises(ObjectNotFoundError):
            item_get_selector(user_a.company, item_b.uuid)
