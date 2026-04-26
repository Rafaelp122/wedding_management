from uuid import UUID

from django.http import HttpRequest

from apps.core.exceptions import ObjectNotFoundError
from apps.core.types import AuthContextUser
from apps.finances.models.budget import Budget
from apps.finances.models.budget_category import BudgetCategory
from apps.finances.models.expense import Expense
from apps.finances.models.installment import Installment
from apps.logistics.models.contract import Contract
from apps.logistics.models.item import Item
from apps.logistics.models.supplier import Supplier
from apps.scheduler.models import Event, Task
from apps.weddings.models import Wedding


# --- RESOLVERS (Usados por Services para resolver dependências internas) ---
def resolve_wedding_for_user(
    user: AuthContextUser, wedding: Wedding | UUID | str
) -> Wedding:
    if isinstance(wedding, Wedding):
        return wedding

    instance = Wedding.objects.for_user(user).filter(uuid=wedding).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Casamento não encontrado ou acesso negado.",
            code="wedding_not_found_or_denied",
        )
    return instance


def resolve_supplier_for_user(
    user: AuthContextUser, supplier: Supplier | UUID | str
) -> Supplier:
    if isinstance(supplier, Supplier):
        return supplier

    instance = Supplier.objects.for_user(user).filter(uuid=supplier).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Fornecedor não encontrado ou acesso negado.",
            code="supplier_not_found_or_denied",
        )
    return instance


def resolve_contract_for_user(
    user: AuthContextUser, contract: Contract | UUID | str
) -> Contract:
    if isinstance(contract, Contract):
        return contract

    instance = Contract.objects.for_user(user).filter(uuid=contract).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Contrato não encontrado ou acesso negado.",
            code="contract_not_found_or_denied",
        )
    return instance


def resolve_budget_category_for_user(
    user: AuthContextUser, category: BudgetCategory | UUID | str
) -> BudgetCategory:
    if isinstance(category, BudgetCategory):
        return category

    instance = BudgetCategory.objects.for_user(user).filter(uuid=category).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Categoria de orçamento não encontrada ou acesso negado.",
            code="budget_category_not_found_or_denied",
        )
    return instance


def resolve_expense_for_user(
    user: AuthContextUser, expense: Expense | UUID | str
) -> Expense:
    if isinstance(expense, Expense):
        return expense

    instance = Expense.objects.for_user(user).filter(uuid=expense).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Despesa não encontrada ou acesso negado.",
            code="expense_not_found_or_denied",
        )
    return instance


# --- DEPENDENCIES (Wrappers para o Ninja Controller / Auditoria de Segurança) ---
def get_wedding(request: HttpRequest, wedding_uuid: UUID) -> Wedding:
    return resolve_wedding_for_user(request.user, wedding_uuid)


def get_supplier(request: HttpRequest, supplier_uuid: UUID) -> Supplier:
    return resolve_supplier_for_user(request.user, supplier_uuid)


def get_contract(request: HttpRequest, contract_uuid: UUID) -> Contract:
    return resolve_contract_for_user(request.user, contract_uuid)


def get_item(request: HttpRequest, item_uuid: UUID) -> Item:
    # Item é um recurso terminal (não possui resolve_ interno por enquanto)
    instance = Item.objects.for_user(request.user).filter(uuid=item_uuid).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Item não encontrado ou acesso negado.",
            code="item_not_found_or_denied",
        )
    return instance


def get_budget_category(request: HttpRequest, category_uuid: UUID) -> BudgetCategory:
    return resolve_budget_category_for_user(request.user, category_uuid)


def get_budget(request: HttpRequest, budget_uuid: UUID) -> Budget:
    instance = Budget.objects.for_user(request.user).filter(uuid=budget_uuid).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Orçamento não encontrado ou acesso negado.",
            code="budget_not_found_or_denied",
        )
    return instance


def get_expense(request: HttpRequest, expense_uuid: UUID) -> Expense:
    return resolve_expense_for_user(request.user, expense_uuid)


def get_installment(request: HttpRequest, installment_uuid: UUID) -> Installment:
    instance = (
        Installment.objects.for_user(request.user).filter(uuid=installment_uuid).first()
    )
    if not instance:
        raise ObjectNotFoundError(
            detail="Parcela não encontrada ou acesso negado.",
            code="installment_not_found_or_denied",
        )
    return instance


def get_event(request: HttpRequest, event_uuid: UUID) -> Event:
    instance = Event.objects.for_user(request.user).filter(uuid=event_uuid).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Evento não encontrado ou acesso negado.",
            code="event_not_found_or_denied",
        )
    return instance


def get_task(request: HttpRequest, task_uuid: UUID) -> Task:
    instance = Task.objects.for_user(request.user).filter(uuid=task_uuid).first()
    if not instance:
        raise ObjectNotFoundError(
            detail="Tarefa não encontrada ou acesso negado.",
            code="task_not_found_or_denied",
        )
    return instance
