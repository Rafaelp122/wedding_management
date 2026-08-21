"""
Testes unitários e de integração para Custom QuerySets e Selectors do app logistics.
Valida isolamento multi-tenant, encadeamento de métodos, anotações de totais e filtros.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, cast
from uuid import uuid4

import pytest

from apps.core.exceptions import ObjectNotFoundError
from apps.finances.models import Installment
from apps.finances.tests.factories import (
    BudgetCategoryFactory as _BudgetCategoryFactory,
)
from apps.finances.tests.factories import (
    BudgetFactory as _BudgetFactory,
)
from apps.finances.tests.factories import (
    ExpenseFactory as _ExpenseFactory,
)
from apps.finances.tests.factories import (
    InstallmentFactory as _InstallmentFactory,
)
from apps.logistics.managers import (
    ContractQuerySet,
    ItemQuerySet,
    SupplierQuerySet,
)
from apps.logistics.models import Contract, Item, Supplier
from apps.logistics.selectors import (
    contract_get_selector,
    contract_list_selector,
    contract_pending_count_selector,
    item_get_selector,
    item_list_selector,
    supplier_get_selector,
    supplier_list_selector,
)
from apps.logistics.tests.factories import (
    ContractFactory as _ContractFactory,
)
from apps.logistics.tests.factories import (
    ItemFactory as _ItemFactory,
)
from apps.logistics.tests.factories import (
    SupplierFactory as _SupplierFactory,
)
from apps.users.models import User
from apps.users.tests.factories import UserFactory as _UserFactory
from apps.weddings.models import Wedding
from apps.weddings.tests.factories import WeddingFactory as _WeddingFactory


def BudgetCategoryFactory(*args: Any, **kwargs: Any) -> Any:
    return _BudgetCategoryFactory(*args, **kwargs)


def BudgetFactory(*args: Any, **kwargs: Any) -> Any:
    return _BudgetFactory(*args, **kwargs)


def ExpenseFactory(*args: Any, **kwargs: Any) -> Any:
    return _ExpenseFactory(*args, **kwargs)


def InstallmentFactory(*args: Any, **kwargs: Any) -> Installment:
    return cast(Installment, _InstallmentFactory(*args, **kwargs))


def ContractFactory(*args: Any, **kwargs: Any) -> Contract:
    return cast(Contract, _ContractFactory(*args, **kwargs))


def ItemFactory(*args: Any, **kwargs: Any) -> Item:
    return cast(Item, _ItemFactory(*args, **kwargs))


def SupplierFactory(*args: Any, **kwargs: Any) -> Supplier:
    return cast(Supplier, _SupplierFactory(*args, **kwargs))


def UserFactory(*args: Any, **kwargs: Any) -> User:
    return cast(User, _UserFactory(*args, **kwargs))


def WeddingFactory(*args: Any, **kwargs: Any) -> Wedding:
    return cast(Wedding, _WeddingFactory(*args, **kwargs))


# ==============================================================================
# TESTES DE CUSTOM QUERYSETS ENCADEÁVEIS
# ==============================================================================


@pytest.mark.django_db
class TestSupplierQuerySet:
    """Testes dos métodos de SupplierQuerySet e seu encadeamento."""

    def test_with_contracts_count(self, user: User) -> None:
        """Anotação contracts_count contabiliza corretamente contratos."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company)
        _ContractFactory.create_batch(
            2, wedding=wedding, company=user.company, supplier=supplier
        )

        qs = Supplier.objects.for_tenant(user.company).with_contracts_count()
        assert isinstance(qs, SupplierQuerySet)
        res = qs.get(uuid=supplier.uuid)
        assert cast(Any, res).contracts_count == 2

    def test_search_by_name_cnpj_email_phone(self, user: User) -> None:
        """Busca textual por nome, CNPJ, e-mail e telefone."""
        SupplierFactory(
            company=user.company,
            name="Buffet Estrela",
            cnpj="11.222.333/0001-44",
            email="contato@estrela.com",
            phone="11999990000",
        )
        SupplierFactory(
            company=user.company,
            name="Decoração Lua",
            cnpj="99.888.777/0001-66",
            email="lua@decor.com",
            phone="21988880000",
        )

        qs = Supplier.objects.for_tenant(user.company)
        assert qs.search("Estrela").count() == 1
        assert qs.search("11.222").count() == 1
        assert qs.search("lua@decor").count() == 1
        assert qs.search("999990000").count() == 1
        assert qs.search("Inexistente").count() == 0
        assert qs.search("").count() == 2

    def test_chaining_supplier_queryset(self, user: User) -> None:
        """Garante encadeamento fluente de métodos em SupplierQuerySet."""
        wedding = WeddingFactory(user_context=user)
        s1 = SupplierFactory(company=user.company, name="Buffet Alfa", is_active=True)
        SupplierFactory(company=user.company, name="Buffet Beta", is_active=False)
        ContractFactory(wedding=wedding, company=user.company, supplier=s1)

        qs = (
            Supplier.objects.for_tenant(user.company)
            .search("Buffet")
            .filter(is_active=True)
            .with_contracts_count()
        )
        assert qs.count() == 1
        first = qs.first()
        assert first is not None
        assert first.name == "Buffet Alfa"
        assert cast(Any, first).contracts_count == 1


@pytest.mark.django_db
class TestContractQuerySet:
    """Testes dos métodos de ContractQuerySet e seu encadeamento."""

    def test_with_totals_annotations(self, user: User) -> None:
        """with_totals anota supplier_name, expense_id, total_paid e addendums_count."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(
            company=user.company, name="Buffet Real", phone="119999", email="b@real.com"
        )
        parent = ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier,
            total_amount=Decimal("1000.00"),
        )
        _ContractFactory.create_batch(
            2, wedding=wedding, company=user.company, supplier=supplier, parent=parent
        )

        budget = BudgetFactory(wedding=wedding)
        cat = BudgetCategoryFactory(budget=budget, wedding=wedding)
        expense = ExpenseFactory(wedding=wedding, category=cat, contract=parent)
        InstallmentFactory(
            expense=expense,
            amount=Decimal("400.00"),
            status=Installment.StatusChoices.PAID,
            paid_date=date.today(),
        )

        qs = Contract.objects.for_tenant(user.company).with_totals()
        assert isinstance(qs, ContractQuerySet)
        c = qs.get(uuid=parent.uuid)
        assert cast(Any, c).supplier_name == "Buffet Real"
        assert cast(Any, c).supplier_phone == "119999"
        assert cast(Any, c).supplier_email == "b@real.com"
        assert cast(Any, c).expense_id == expense.uuid
        assert cast(Any, c).total_paid == Decimal("400.00")
        assert cast(Any, c).addendums_count == 2
        assert cast(Any, c).addendums_total_amount == Decimal("10000.00")

    def test_by_status(self, user: User) -> None:
        """by_status filtra pelo status informado."""
        wedding = WeddingFactory(user_context=user)
        ContractFactory(
            wedding=wedding, company=user.company, status=Contract.StatusChoices.DRAFT
        )
        ContractFactory(
            wedding=wedding, company=user.company, status=Contract.StatusChoices.PENDING
        )

        qs = Contract.objects.for_tenant(user.company)
        assert qs.by_status(Contract.StatusChoices.DRAFT).count() == 1
        assert qs.by_status(Contract.StatusChoices.PENDING).count() == 1
        assert qs.by_status(None).count() == 2

    def test_for_wedding(self, user: User) -> None:
        """for_wedding aceita Wedding, UUID e str."""
        w1 = WeddingFactory(user_context=user)
        w2 = WeddingFactory(user_context=user)
        c1 = ContractFactory(wedding=w1, company=user.company)
        c2 = ContractFactory(wedding=w2, company=user.company)

        qs = Contract.objects.for_tenant(user.company)
        assert qs.for_wedding(w1).count() == 1
        assert qs.for_wedding(w1.uuid).first() == c1
        assert qs.for_wedding(str(w2.uuid)).first() == c2
        assert qs.for_wedding(None).count() == 2


@pytest.mark.django_db
class TestContractItemQuerySet:
    """Testes dos métodos de ContractItemQuerySet e seu encadeamento."""

    def test_for_contract(self, user: User) -> None:
        """for_contract aceita Contract, UUID e str."""
        wedding = WeddingFactory(user_context=user)
        c1 = ContractFactory(wedding=wedding, company=user.company)
        c2 = ContractFactory(wedding=wedding, company=user.company)
        ItemFactory(wedding=wedding, contract=c1, company=user.company)
        ItemFactory(wedding=wedding, contract=c2, company=user.company)

        qs = Item.objects.for_tenant(user.company)
        assert isinstance(qs, ItemQuerySet)
        assert qs.for_contract(c1).count() == 1
        assert qs.for_contract(c1.uuid).count() == 1
        assert qs.for_contract(str(c2.uuid)).count() == 1
        assert qs.for_contract(None).count() == 2

    def test_chaining_item_queryset(self, user: User) -> None:
        """Testa encadeamento de filtros em itens."""
        wedding = WeddingFactory(user_context=user)
        c = ContractFactory(wedding=wedding, company=user.company)
        ItemFactory(
            wedding=wedding,
            contract=c,
            company=user.company,
            name="Cadeiras Tiffany",
            acquisition_status=Item.AcquisitionStatus.IN_PROGRESS,
        )
        ItemFactory(
            wedding=wedding,
            contract=c,
            company=user.company,
            name="Mesa Principal",
            acquisition_status=Item.AcquisitionStatus.DONE,
        )

        qs = (
            Item.objects.for_tenant(user.company)
            .for_wedding(wedding)
            .for_contract(c)
            .by_status(Item.AcquisitionStatus.IN_PROGRESS)
            .search("Cadeiras")
            .with_details()
        )
        assert qs.count() == 1
        first = qs.first()
        assert first is not None
        assert first.name == "Cadeiras Tiffany"


# ==============================================================================
# TESTES DE SELECTORS DO DOMÍNIO SUPPLIERS
# ==============================================================================


@pytest.mark.django_db
class TestSupplierSelectors:
    """Testes para os seletores de leitura de fornecedores."""

    def test_supplier_list_selector_multitenancy(self) -> None:
        """supplier_list_selector respeita isolamento multitenant."""
        user_a = UserFactory()
        user_b = UserFactory()

        SupplierFactory(company=user_a.company, name="Fornecedor A")
        SupplierFactory(company=user_b.company, name="Fornecedor B")

        qs_a = supplier_list_selector(user_a.company)
        assert qs_a.count() == 1
        supp_a = qs_a.first()
        assert supp_a is not None and supp_a.name == "Fornecedor A"

        qs_b = supplier_list_selector(user_b.company)
        assert qs_b.count() == 1
        supp_b = qs_b.first()
        assert supp_b is not None and supp_b.name == "Fornecedor B"

    def test_supplier_list_selector_filters(self, user: User) -> None:
        """supplier_list_selector filtra por busca e status ativo."""
        SupplierFactory(company=user.company, name="Doceria Doce", is_active=True)
        SupplierFactory(company=user.company, name="Doceria Salgada", is_active=False)

        assert supplier_list_selector(user.company, search="Doceria").count() == 2
        assert (
            supplier_list_selector(user.company, search="Doce", is_active=True).count()
            == 1
        )
        assert supplier_list_selector(user.company, is_active=False).count() == 1

    def test_supplier_get_selector_success(self, user: User) -> None:
        """supplier_get_selector retorna fornecedor correto."""
        supplier = SupplierFactory(company=user.company, name="Banda Som")
        res = supplier_get_selector(user.company, supplier.uuid)
        assert res.uuid == supplier.uuid
        assert res.name == "Banda Som"

    def test_supplier_get_selector_not_found(self, user: User) -> None:
        """supplier_get_selector levanta ObjectNotFoundError para UUID inexistente."""
        with pytest.raises(ObjectNotFoundError):
            supplier_get_selector(user.company, uuid4())

    def test_supplier_get_selector_multitenancy(self) -> None:
        """supplier_get_selector impede acesso cruzado entre empresas."""
        user_a = UserFactory()
        user_b = UserFactory()
        supplier_b = SupplierFactory(company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            supplier_get_selector(user_a.company, supplier_b.uuid)


# ==============================================================================
# TESTES DE SELECTORS DO DOMÍNIO CONTRACTS
# ==============================================================================


@pytest.mark.django_db
class TestContractSelectors:
    """Testes para os seletores de leitura de contratos."""

    def test_contract_list_selector_multitenancy(self) -> None:
        """contract_list_selector retorna apenas contratos da empresa."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_a = WeddingFactory(user_context=user_a)
        wedding_b = WeddingFactory(user_context=user_b)
        ContractFactory(wedding=wedding_a, company=user_a.company)
        ContractFactory(wedding=wedding_b, company=user_b.company)

        assert contract_list_selector(user_a.company).count() == 1
        assert contract_list_selector(user_b.company).count() == 1

    def test_contract_list_selector_filters(self, user: User) -> None:
        """contract_list_selector aplica wedding_id, status, supplier_id e parent_id."""
        wedding = WeddingFactory(user_context=user)
        supplier1 = SupplierFactory(company=user.company)
        supplier2 = SupplierFactory(company=user.company)
        parent = ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier1,
            status=Contract.StatusChoices.DRAFT,
        )
        ContractFactory(
            wedding=wedding,
            company=user.company,
            supplier=supplier2,
            parent=parent,
            status=Contract.StatusChoices.PENDING,
        )

        assert (
            contract_list_selector(user.company, wedding_id=wedding.uuid).count() == 2
        )
        assert (
            contract_list_selector(
                user.company, status=Contract.StatusChoices.DRAFT
            ).count()
            == 1
        )
        assert (
            contract_list_selector(user.company, supplier_id=supplier2.uuid).count()
            == 1
        )
        assert contract_list_selector(user.company, parent_id=parent.uuid).count() == 1

    def test_contract_get_selector_success(self, user: User) -> None:
        """contract_get_selector retorna contrato com totais anotados."""
        wedding = WeddingFactory(user_context=user)
        supplier = SupplierFactory(company=user.company, name="Floricultura")
        contract = ContractFactory(
            wedding=wedding, company=user.company, supplier=supplier
        )

        res = contract_get_selector(user.company, contract.uuid)
        assert res.uuid == contract.uuid
        assert cast(Any, res).supplier_name == "Floricultura"

    def test_contract_get_selector_not_found_and_multitenancy(self) -> None:
        """contract_get_selector valida inexistência e cross-tenant."""
        user_a = UserFactory()
        user_b = UserFactory()
        wedding_b = WeddingFactory(user_context=user_b)
        contract_b = ContractFactory(wedding=wedding_b, company=user_b.company)

        with pytest.raises(ObjectNotFoundError):
            contract_get_selector(user_a.company, uuid4())

        with pytest.raises(ObjectNotFoundError):
            contract_get_selector(user_a.company, contract_b.uuid)

    def test_contract_pending_count_selector(self, user: User) -> None:
        """contract_pending_count_selector conta apenas contratos PENDING."""
        wedding = WeddingFactory(user_context=user)
        ContractFactory(
            wedding=wedding, company=user.company, status=Contract.StatusChoices.PENDING
        )
        ContractFactory(
            wedding=wedding, company=user.company, status=Contract.StatusChoices.PENDING
        )
        ContractFactory(
            wedding=wedding, company=user.company, status=Contract.StatusChoices.DRAFT
        )

        assert contract_pending_count_selector(user.company) == 2
        assert (
            contract_pending_count_selector(user.company, wedding_id=wedding.uuid) == 2
        )


# ==============================================================================
# TESTES DE SELECTORS DO DOMÍNIO ITEMS
# ==============================================================================


@pytest.mark.django_db
class TestItemSelectors:
    """Testes para os seletores de leitura de itens de logística."""

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
        """
        item_list_selector filtra por casamento, status, busca e contrato.
        """
        wedding = WeddingFactory(user_context=user)
        contract = ContractFactory(wedding=wedding, company=user.company)
        ItemFactory(
            wedding=wedding,
            contract=contract,
            company=user.company,
            name="Taças de Cristal",
            acquisition_status=Item.AcquisitionStatus.DONE,
        )
        ItemFactory(
            wedding=wedding,
            contract=None,
            company=user.company,
            name="Pratos Rasos",
            acquisition_status=Item.AcquisitionStatus.PENDING,
        )

        assert item_list_selector(user.company, wedding_id=wedding.uuid).count() == 2
        assert (
            item_list_selector(user.company, status=Item.AcquisitionStatus.DONE).count()
            == 1
        )
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
