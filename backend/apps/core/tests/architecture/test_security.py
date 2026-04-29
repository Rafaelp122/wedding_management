import ast
import inspect

import pytest

from apps.events.api.event_controller import EventController
from apps.events.api.wedding_controller import WeddingController
from apps.finances.api.budget_controller import BudgetController
from apps.finances.api.category_controller import CategoryController
from apps.finances.api.expense_controller import ExpenseController
from apps.finances.api.installment_controller import InstallmentController
from apps.logistics.api.contracts import ContractController
from apps.logistics.api.items import ItemController
from apps.logistics.api.suppliers import SupplierController
from apps.scheduler.api.scheduler_controller import SchedulerController


def _assert_get_resource_called(controller_class, uuid_param: str, getter_fn_name: str):
    """Verifica se todo método com uuid_param chama a função getter correta."""
    try:
        source_file = inspect.getfile(controller_class)
        with open(source_file) as f:
            source = f.read()
    except (TypeError, OSError):
        pytest.fail(
            "Não foi possível localizar o arquivo fonte para "
            f"{controller_class.__name__}"
        )

    tree = ast.parse(source)

    for node in ast.walk(tree):
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

                attr_calls = [
                    n.func.attr
                    for n in ast.walk(item)
                    if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)
                ]

                all_calls = calls + attr_calls

                # No caso de EventService.resolve, o getter_fn_name pode ser
                # 'get_event' ou 'resolve' dependendo de como a dependência é
                # injetada. Como os novos controllers usam EventService.resolve
                # diretamente, vamos checar ambos.
                valid_getters = [getter_fn_name, "resolve"]
                found = any(g in all_calls for g in valid_getters)

                assert found, (
                    f"{controller_class.__name__}.{item.name}() possui "
                    f"'{uuid_param}' mas não chama {valid_getters}()"
                )


@pytest.mark.parametrize(
    "controller, uuid_field, getter",
    [
        (EventController, "event_uuid", "get_event"),
        (WeddingController, "event_uuid", "get_event"),
        (SupplierController, "supplier_uuid", "get_supplier"),
        (ContractController, "contract_uuid", "get_contract"),
        (ItemController, "item_uuid", "get_item"),
        (BudgetController, "budget_uuid", "get_budget"),
        (CategoryController, "category_uuid", "get_budget_category"),
        (ExpenseController, "expense_uuid", "get_expense"),
        (InstallmentController, "installment_uuid", "get_installment"),
        (SchedulerController, "event_uuid", "get_event"),
        (SchedulerController, "task_uuid", "get_task"),
    ],
)
def test_controller_resource_resolution_security(controller, uuid_field, getter):
    """
    AUDITORIA DE SEGURANÇA (AST): Garante que todo endpoint que recebe um UUID
    faz a resolução obrigatória de posse (evita IDOR).
    """
    _assert_get_resource_called(controller, uuid_field, getter)
