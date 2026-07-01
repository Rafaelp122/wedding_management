import pytest
from uuid import UUID
from decimal import Decimal
from django.test.utils import CaptureQueriesContext
from django.db import connection
from apps.finances.models import Expense, Budget, BudgetCategory, Installment
from apps.finances.schemas import ExpenseOut, BudgetOut, BudgetCategoryOut
from apps.finances.tests.factories import ExpenseFactory, InstallmentFactory, BudgetCategoryFactory, BudgetFactory
from apps.tenants.models import Company
from apps.weddings.tests.factories import WeddingFactory

@pytest.mark.django_db
def test_benchmark_n_plus_one_resolved():
    print("\n--- ⚡ Iniciando Benchmark de Performance (Verificação de Correção) ---")

    # 1. Setup Data
    company = Company.objects.create(name="Benchmarking Co", slug="benchmarking-co")
    wedding = WeddingFactory(company=company)
    budget = BudgetFactory(wedding=wedding, company=company)

    categories = BudgetCategoryFactory.create_batch(5, budget=budget, wedding=wedding, company=company)

    # Criar 10 despesas, cada uma com 3 parcelas (2 pagas)
    expenses = []
    from django.utils import timezone
    for i in range(10):
        exp = ExpenseFactory(wedding=wedding, company=company, category=categories[i % 5], actual_amount=Decimal("300.00"))
        # Force create installments
        exp.installments.all().delete()
        InstallmentFactory.create_batch(
            2,
            expense=exp,
            status=Installment.StatusChoices.PAID,
            amount=Decimal("100.00"),
            paid_date=timezone.now().date()
        )
        InstallmentFactory.create_batch(1, expense=exp, status=Installment.StatusChoices.PENDING, amount=Decimal("100.00"))
        expenses.append(exp)

    print(f"Dados criados: 1 Budget, {len(categories)} Categorias, {len(expenses)} Despesas.")

    # 2. Verificar ExpenseOut
    print("\n--- Verificando ExpenseOut ---")

    # Caso Otimizado: COM with_details()
    expenses_optimized = Expense.objects.filter(id__in=[e.id for e in expenses]).with_details()

    with CaptureQueriesContext(connection) as ctx:
        list_optimized = list(expenses_optimized)
        queries_before_resolve = len(ctx)

        for exp in list_optimized:
            ExpenseOut.from_orm(exp)

    total_queries = len(ctx)
    extra_queries = total_queries - queries_before_resolve
    print(f"Queries para 10 ExpenseOut (COM with_details): {total_queries} (Sendo {extra_queries} extras)")

    assert extra_queries == 0, f"Deveria haver 0 queries extras, mas houve {extra_queries}!"

    # 3. Verificar BudgetCategoryOut
    print("\n--- Verificando BudgetCategoryOut ---")
    categories_optimized = BudgetCategory.objects.filter(id__in=[c.id for c in categories]).with_total_spent().select_related("wedding", "budget")

    with CaptureQueriesContext(connection) as ctx:
        list_cats = list(categories_optimized)
        queries_before_resolve = len(ctx)
        for cat in list_cats:
            print(f"Resolvendo categoria: {cat.name}")
            BudgetCategoryOut.from_orm(cat)
        for query in ctx.captured_queries[queries_before_resolve:]:
            print(f"QUERY EXTRA: {query['sql']}")

    extra_queries_cat = len(ctx) - queries_before_resolve
    print(f"Queries para {len(categories)} Categorias (COM with_total_spent): {len(ctx)} (Sendo {extra_queries_cat} extras)")
    assert extra_queries_cat == 0, "N+1 detectado em BudgetCategoryOut!"

    # 4. Verificar BudgetOut
    print("\n--- Verificando BudgetOut ---")
    budget_optimized = Budget.objects.filter(id=budget.id).with_total_spent().select_related("wedding")

    with CaptureQueriesContext(connection) as ctx:
        b_inst = list(budget_optimized)[0]
        queries_before_resolve = len(ctx)
        BudgetOut.from_orm(b_inst)

    extra_queries_budget = len(ctx) - queries_before_resolve
    print(f"Queries para 1 Budget (COM with_total_spent): {len(ctx)} (Sendo {extra_queries_budget} extras)")
    assert extra_queries_budget == 0, "N+1 detectado em BudgetOut!"

    # 5. Verificação de Integridade de Dados (UUIDs)
    print("\n--- Verificando Integridade de Dados (UUIDs) ---")
    expense_data = ExpenseOut.from_orm(expenses[0])
    assert isinstance(expense_data.wedding, UUID), f"Wedding deve ser UUID, veio {type(expense_data.wedding)}"
    assert expense_data.wedding == wedding.uuid

    if expenses[0].contract_id:
        assert isinstance(expense_data.contract, UUID)

    print("✅ Integridade de dados (UUIDs) confirmada!")

    print("\n--- Verificação Finalizada com Sucesso! ---")
