from django.http import HttpRequest
from ninja import Router
from ninja.pagination import paginate
from pydantic import UUID4

from apps.core.constants import MUTATION_ERROR_RESPONSES, READ_ERROR_RESPONSES
from apps.finances.schemas import (
    BudgetCategoryIn,
    BudgetCategoryOut,
    BudgetCategoryPatchIn,
    BudgetIn,
    BudgetOut,
    BudgetPatchIn,
    ExpenseIn,
    ExpenseOut,
    ExpensePatchIn,
    InstallmentIn,
    InstallmentOut,
    InstallmentPatchIn,
)
from apps.finances.services.budget_category_service import BudgetCategoryService
from apps.finances.services.budget_service import BudgetService
from apps.finances.services.expense_service import ExpenseService
from apps.finances.services.installment_service import InstallmentService


# --- ROUTERS ---
budgets_router = Router(tags=["Finances"])
budget_categories_router = Router(tags=["Finances"])
expenses_router = Router(tags=["Finances"])
installments_router = Router(tags=["Finances"])


# --- BUDGET ENDPOINTS ---
@budgets_router.get("/", response=list[BudgetOut], operation_id="finances_budgets_list")
@paginate
def list_budgets(request: HttpRequest):
    """
    Lista as estatísticas de orçamento geral de todos os casamentos.
    """
    return BudgetService.list(request.user)


@budgets_router.get(
    "/{uuid}/",
    response={200: BudgetOut, **READ_ERROR_RESPONSES},
    operation_id="finances_budgets_read",
)
def get_budget(request: HttpRequest, uuid: UUID4):
    """
    Retorna os totais e os saldos remanescentes autorizados de um projeto macro.
    """
    return BudgetService.get(request.user, uuid)


@budgets_router.post(
    "/",
    response={201: BudgetOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_create",
)
def create_budget(request: HttpRequest, payload: BudgetIn):
    """
    Dá pontapé inicial para a planilha contábil centralizada.
    Atrelada às métricas cerimoniais.
    """
    return 201, BudgetService.create(request.user, payload.dict())


@budgets_router.patch(
    "/{uuid}/",
    response={200: BudgetOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_partial_update",
)
def partial_update_budget(request: HttpRequest, uuid: UUID4, payload: BudgetPatchIn):
    """
    Atualiza métricas mestres de gasto e painéis globais.
    Contorna referências numéricas totais.
    """
    instance = BudgetService.get(request.user, uuid)
    return BudgetService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@budgets_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_budgets_delete",
)
def delete_budget(request: HttpRequest, uuid: UUID4):
    """
    Remove toda e qualquer anotação da malha financeira.
    Varre as despesas em ação de reverso total absoluto.
    """
    instance = BudgetService.get(request.user, uuid)
    BudgetService.delete(request.user, instance)
    return 204, None


# --- BUDGET CATEGORY ENDPOINTS ---
@budget_categories_router.get(
    "/", response=list[BudgetCategoryOut], operation_id="finances_categories_list"
)
@paginate
def list_categories(request: HttpRequest):
    """
    Exibe todos os módulos separadores de custos, como Buffet e Cerimonial.
    """
    return BudgetCategoryService.list(request.user)


@budget_categories_router.get(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **READ_ERROR_RESPONSES},
    operation_id="finances_categories_read",
)
def get_category(request: HttpRequest, uuid: UUID4):
    """
    Acessa os detalhamentos da categoria isolada de forma simples e visual.
    Garante a segurança contábil sem vazar detalhes restritos a terceiros.
    """
    return BudgetCategoryService.get(request.user, uuid)


@budget_categories_router.post(
    "/",
    response={201: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_create",
)
def create_category(request: HttpRequest, payload: BudgetCategoryIn):
    """
    Abre mais um bloco de centro de custo em conta específica da festa.
    Associa devidamente ao orçamento atrelado em tela.
    """
    return 201, BudgetCategoryService.create(request.user, payload.dict())


@budget_categories_router.patch(
    "/{uuid}/",
    response={200: BudgetCategoryOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_partial_update",
)
def partial_update_category(
    request: HttpRequest, uuid: UUID4, payload: BudgetCategoryPatchIn
):
    """
    Corrige o título, ou altera o valor dos gastos planejados.
    Evita sobrescrições acidentais errôneas em outras rotas.
    """
    instance = BudgetCategoryService.get(request.user, uuid)
    return BudgetCategoryService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@budget_categories_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_categories_delete",
)
def delete_category(request: HttpRequest, uuid: UUID4):
    """
    Fecha um agrupamento no orçamento permanentemente.
    Exclui anotações de faturas de modo destrutivo para balanceamento.
    """
    instance = BudgetCategoryService.get(request.user, uuid)
    BudgetCategoryService.delete(request.user, instance)
    return 204, None


# --- EXPENSE ENDPOINTS ---
@expenses_router.get(
    "/", response=list[ExpenseOut], operation_id="finances_expenses_list"
)
@paginate
def list_expenses(request: HttpRequest):
    """
    Lista todas as compras e despachos que saíram dos painéis orçamentários.
    """
    return ExpenseService.list(request.user)


@expenses_router.get(
    "/{uuid}/",
    response={200: ExpenseOut, **READ_ERROR_RESPONSES},
    operation_id="finances_expenses_read",
)
def get_expense(request: HttpRequest, uuid: UUID4):
    """
    Retorna recibo unitário simplificado nominal registrado no controle base.
    """
    return ExpenseService.get(request.user, uuid)


@expenses_router.post(
    "/",
    response={201: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_create",
)
def create_expense(request: HttpRequest, payload: ExpenseIn):
    """
    Aprova lançamento final nos tetos das divisões e categorias.
    Consome o limite orçamentário previsto inicial geral da categoria.
    """
    return 201, ExpenseService.create(request.user, payload.dict())


@expenses_router.patch(
    "/{uuid}/",
    response={200: ExpenseOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_partial_update",
)
def partial_update_expense(request: HttpRequest, uuid: UUID4, payload: ExpensePatchIn):
    """
    Ajuste na conta para valores fracionários sem afetar o fluxo contábil.
    """
    instance = ExpenseService.get(request.user, uuid)
    return ExpenseService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@expenses_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_expenses_delete",
)
def delete_expense(request: HttpRequest, uuid: UUID4):
    """
    Deleta uma compra revertendo seu efeito, estornando em painel os gastos.
    """
    instance = ExpenseService.get(request.user, uuid)
    ExpenseService.delete(request.user, instance)
    return 204, None


# --- INSTALLMENT ENDPOINTS ---
@installments_router.get(
    "/", response=list[InstallmentOut], operation_id="finances_installments_list"
)
@paginate
def list_installments(request: HttpRequest):
    """
    Lista faturas fragmentadas originárias para os fluxos pendentes.
    Faturas isoladas ligadas a pagamentos unificados.
    """
    return InstallmentService.list(request.user)


@installments_router.get(
    "/{uuid}/",
    response={200: InstallmentOut, **READ_ERROR_RESPONSES},
    operation_id="finances_installments_read",
)
def get_installment(request: HttpRequest, uuid: UUID4):
    """
    Revela notas fragmentais e guias pendentes programados do recebimento.
    """
    return InstallmentService.get(request.user, uuid)


@installments_router.post(
    "/",
    response={201: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_create",
)
def create_installment(request: HttpRequest, payload: InstallmentIn):
    """
    Grava pendências parciais atestando dependências de transações.
    """
    return 201, InstallmentService.create(request.user, payload.dict())


@installments_router.patch(
    "/{uuid}/",
    response={200: InstallmentOut, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_partial_update",
)
def partial_update_installment(
    request: HttpRequest, uuid: UUID4, payload: InstallmentPatchIn
):
    """
    Edita temporalmente ou encerra status validando com pagamento de guia as etapas.
    """
    instance = InstallmentService.get(request.user, uuid)
    return InstallmentService.partial_update(
        request.user, instance, payload.dict(exclude_unset=True)
    )


@installments_router.delete(
    "/{uuid}/",
    response={204: None, **MUTATION_ERROR_RESPONSES},
    operation_id="finances_installments_delete",
)
def delete_installment(request: HttpRequest, uuid: UUID4):
    """
    Exclui registro pendente restabelecendo ordem das cobranças integrando-as.
    """
    instance = InstallmentService.get(request.user, uuid)
    InstallmentService.delete(request.user, instance)
    return 204, None
