import { lazy, Suspense, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useFinancesExpensesList,
  getFinancesBudgetsForWeddingQueryKey,
  getFinancesCategoriesListQueryKey,
  getFinancesExpensesListQueryKey,
} from "@/api/generated/v1/endpoints/finances/finances";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import { useWeddingBudget } from "@/features/finances/hooks/useBudget";
import { WeddingFinancesSummaryCards } from "./FinancesSummaryCards";
import { WeddingFinancesGroupsSummary } from "./FinancesGroupsSummary";
import { WeddingFinancesRecentExpenses } from "./expenses/FinancesRecentExpenses";
import { WeddingExpensesTable } from "./expenses/ExpensesTable";
import { Skeleton } from "@/components/ui/skeleton";

const WeddingFinancesDistributionChart = lazy(
  () =>
    import("./FinancesDistributionChart").then((m) => ({
      default: m.WeddingFinancesDistributionChart,
    })),
);

const CreateExpenseDialog = lazy(
  () => import("./expenses/CreateExpenseDialog").then((m) => ({ default: m.CreateExpenseDialog })),
);

const EditExpenseDialog = lazy(
  () => import("./expenses/EditExpenseDialog").then((m) => ({ default: m.EditExpenseDialog })),
);

const DeleteExpenseDialog = lazy(
  () => import("./expenses/DeleteExpenseDialog").then((m) => ({ default: m.DeleteExpenseDialog })),
);

const ExpenseDetailSheet = lazy(
  () => import("./expenses/ExpenseDetailSheet").then((m) => ({ default: m.ExpenseDetailSheet })),
);

interface WeddingFinancesViewProps {
  weddingUuid: string;
}

export function WeddingFinancesView({ weddingUuid }: WeddingFinancesViewProps) {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editingExpense, setEditingExpense] = useState<ExpenseOut | null>(null);
  const [deletingExpense, setDeletingExpense] = useState<ExpenseOut | null>(null);
  const [detailExpense, setDetailExpense] = useState<ExpenseOut | null>(null);
  const queryClient = useQueryClient();

  const {
    categories,
    isLoading: isBudgetLoading,
    totalEstimated,
    totalSpent,
  } = useWeddingBudget(weddingUuid);

  const { data: expensesResponse, isLoading: isExpensesLoading } =
    useFinancesExpensesList({ wedding_id: weddingUuid });

  const { data: recentExpensesResponse, isLoading: isRecentExpensesLoading } =
    useFinancesExpensesList({ wedding_id: weddingUuid, limit: 5 });

  const handleExpenseUpdated = () => {
    queryClient.invalidateQueries({
      queryKey: getFinancesExpensesListQueryKey({ wedding_id: weddingUuid }),
    });
    queryClient.invalidateQueries({
      queryKey: getFinancesExpensesListQueryKey({ wedding_id: weddingUuid, limit: 5 }),
    });
    queryClient.invalidateQueries({
      queryKey: getFinancesBudgetsForWeddingQueryKey(weddingUuid),
    });
    queryClient.invalidateQueries({
      queryKey: getFinancesCategoriesListQueryKey({
        wedding_id: weddingUuid,
      }),
    });
  };

  const handleExpenseCreated = () => {
    setCreateDialogOpen(false);
    handleExpenseUpdated();
  };

  const expenses = expensesResponse?.data?.items || [];
  const recentExpensesItems = recentExpensesResponse?.data?.items || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Resumo Financeiro */}
      {isBudgetLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-28 w-full rounded-xl" />
          <Skeleton className="h-28 w-full rounded-xl" />
          <Skeleton className="h-28 w-full rounded-xl" />
        </div>
      ) : (
        <WeddingFinancesSummaryCards
          totalEstimated={totalEstimated}
          totalSpent={totalSpent}
        />
      )}

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Gráfico de Distribuição */}
        <div className="lg:col-span-3">
          {isBudgetLoading ? (
            <Skeleton className="h-80 w-full rounded-xl" />
          ) : (
            <Suspense fallback={<div className="h-80 rounded-xl bg-muted/20 animate-pulse" />}>
              <WeddingFinancesDistributionChart categories={categories} />
            </Suspense>
          )}
        </div>

        {/* Categorias e Alocação */}
        <div className="lg:col-span-2">
          {isBudgetLoading ? (
            <Skeleton className="h-80 w-full rounded-xl" />
          ) : (
            <WeddingFinancesGroupsSummary
              categories={categories}
              weddingUuid={weddingUuid}
              onCategoryChanged={() => {
                queryClient.invalidateQueries({
                  queryKey: getFinancesCategoriesListQueryKey({
                    wedding_id: weddingUuid,
                  }),
                });
                queryClient.invalidateQueries({
                  queryKey: getFinancesBudgetsForWeddingQueryKey(weddingUuid),
                });
              }}
            />
          )}
        </div>
      </div>

      {/* Despesas Recentes (cards) */}
      {isRecentExpensesLoading ? (
        <Skeleton className="h-48 w-full rounded-xl" />
      ) : (
        <WeddingFinancesRecentExpenses
          expenses={recentExpensesItems}
          onAddExpense={() => setCreateDialogOpen(true)}
        />
      )}

      {/* Todas as Despesas (tabela com ações) */}
      <div>
        {isExpensesLoading ? (
          <Skeleton className="h-64 w-full rounded-xl" />
        ) : (
          <WeddingExpensesTable
            expenses={expenses}
            onEditExpense={setEditingExpense}
            onDeleteExpense={setDeletingExpense}
            onDetailExpense={setDetailExpense}
          />
        )}
      </div>

      <Suspense fallback={null}>
        <CreateExpenseDialog
          weddingUuid={weddingUuid}
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
          onSuccess={handleExpenseCreated}
        />
      </Suspense>

      {editingExpense ? (
        <Suspense fallback={null}>
          <EditExpenseDialog
            expense={editingExpense}
            weddingUuid={weddingUuid}
            open={!!editingExpense}
            onOpenChange={(open) => {
              if (!open) setEditingExpense(null);
            }}
            onSuccess={() => {
              setEditingExpense(null);
              handleExpenseUpdated();
            }}
          />
        </Suspense>
      ) : null}

      {deletingExpense ? (
        <Suspense fallback={null}>
          <DeleteExpenseDialog
            expense={deletingExpense}
            open={!!deletingExpense}
            onOpenChange={(open) => {
              if (!open) setDeletingExpense(null);
            }}
            onSuccess={() => {
              setDeletingExpense(null);
              handleExpenseUpdated();
            }}
          />
        </Suspense>
      ) : null}

      {detailExpense ? (
        <Suspense fallback={null}>
          <ExpenseDetailSheet
            expense={detailExpense}
            open={!!detailExpense}
            onOpenChange={(open) => {
              if (!open) setDetailExpense(null);
            }}
          />
        </Suspense>
      ) : null}
    </div>
  );
}
