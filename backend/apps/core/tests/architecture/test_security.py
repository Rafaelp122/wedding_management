import ast
import inspect

import pytest

from apps.finances.api.finances_controller import FinanceController
from apps.logistics.api.contracts import ContractController
from apps.logistics.api.items import ItemController
from apps.logistics.api.suppliers import SupplierController
from apps.scheduler.api.scheduler_controller import SchedulerController
from apps.weddings.api import WeddingController


def _assert_get_resource_called(controller_class, uuid_param: str, getter_fn_name: str):
    """Verifica se todo método com uuid_param chama a função getter correta."""
    # Tenta obter o arquivo fonte da classe
    try:
        source_file = inspect.getfile(controller_class)
        with open(source_file) as f:
            source = f.read()
    except (TypeError, OSError):
        # Fallback se inspect.getfile falhar
        pytest.fail(
            f"Não foi possível localizar o arquivo fonte para "
            f"{controller_class.__name__}"
        )

    tree = ast.parse(source)

    for node in ast.walk(tree):
        # Procuramos por definições de métodos dentro da classe correspondente
        if isinstance(node, ast.ClassDef) and node.name == controller_class.__name__:
            for item in node.body:
                if not isinstance(item, ast.FunctionDef):
                    continue

                args = [a.arg for a in item.args.args]
                if uuid_param not in args:
                    continue

                calls = [
                    n.func.id
                    for n in ast.walk(item)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
                ]

                # Também verifica se a chamada é feita através de self
                # (ex: self.get_resource)
                attr_calls = [
                    n.func.attr
                    for n in ast.walk(item)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                ]

                all_calls = calls + attr_calls

                assert getter_fn_name in all_calls, (
                    f"{controller_class.__name__}.{item.name}() possui "
                    f"'{uuid_param}' mas não chama {getter_fn_name}()"
                )


def test_wedding_controller_uses_get_wedding():
    _assert_get_resource_called(WeddingController, "wedding_uuid", "get_wedding")


def test_supplier_controller_uses_get_supplier():
    _assert_get_resource_called(SupplierController, "supplier_uuid", "get_supplier")


def test_contract_controller_uses_get_contract():
    _assert_get_resource_called(ContractController, "contract_uuid", "get_contract")


def test_item_controller_uses_get_item():
    _assert_get_resource_called(ItemController, "item_uuid", "get_item")


def test_finance_controller_uses_correct_getters():
    # Verifica todos os UUIDs gerenciados pelo FinanceController unificado
    _assert_get_resource_called(FinanceController, "budget_uuid", "get_budget")
    _assert_get_resource_called(
        FinanceController, "category_uuid", "get_budget_category"
    )
    _assert_get_resource_called(FinanceController, "expense_uuid", "get_expense")
    _assert_get_resource_called(
        FinanceController, "installment_uuid", "get_installment"
    )


def test_scheduler_controller_uses_correct_getters():
    # Verifica todos os UUIDs gerenciados pelo SchedulerController unificado
    _assert_get_resource_called(SchedulerController, "event_uuid", "get_event")
    _assert_get_resource_called(SchedulerController, "task_uuid", "get_task")
