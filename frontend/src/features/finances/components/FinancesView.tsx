import { lazy, Suspense, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  useFinancesExpensesList,
  getFinancesBudgetsForWeddingQueryKey,
  getFinancesCategoriesListQueryKey,
  getFinancesExpensesListQueryKey,
} from "@/api/generated/v1/endpoints/finances/finances";
import { useWeddingBudget } from "../hooks/useBudget";
import { WeddingFinancesSummaryCards } from "./FinancesSummaryCards";
import { WeddingFinancesGroupsSummary } from "./FinancesGroupsSummary";
import { WeddingFinancesRecentExpenses } from "./expenses/FinancesRecentExpenses";
import { WeddingExpensesTable } from "./expenses/ExpensesTable";

const WeddingFinancesDistributionChart = lazy(
  () =>
    import("./FinancesDistributionChart").then((m) => ({
      default: m.WeddingFinancesDistributionChart,
    })),
);

const CreateExpenseDialog = lazy(
  () => import("./expenses/CreateExpenseDialog").then((m) => ({ default: m.CreateExpenseDialog })),
);

interface WeddingFinancesViewProps {
  weddingUuid: string;
}

export function WeddingFinancesView({ weddingUuid }: WeddingFinancesViewProps) {
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const queryClient = useQueryClient();

  const {
    categories,
    isLoading: isBudgetLoading,
    totalEstimated,
    totalSpent,
  } = useWeddingBudget(weddingUuid);

  const { data: expensesResponse, isLoading: isExpensesLoading } =
    useFinancesExpensesList({ wedding_id: weddingUuid });

  const { data: recentExpensesResponse } =
    useFinancesExpensesList({ wedding_id: weddingUuid, limit: 5 });

  const handleExpenseCreated = () => {
    setCreateDialogOpen(false);
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

  if (isBudgetLoading || isExpensesLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <p className="text-zinc-500 animate-pulse">
          Carregando dados financeiros...
        </p>
      </div>
    );
  }

  const expenses = expensesResponse?.data?.items || [];
  const recentExpensesItems = recentExpensesResponse?.data?.items || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Resumo Financeiro */}
      <WeddingFinancesSummaryCards
        totalEstimated={totalEstimated}
        totalSpent={totalSpent}
      />

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Gráfico de Distribuição */}
        <div className="lg:col-span-3">
          <Suspense fallback={<div className="h-80 rounded-xl bg-muted/20 animate-pulse" />}>
            <WeddingFinancesDistributionChart categories={categories} />
          </Suspense>
        </div>

        {/* Categorias e Alocação */}
        <div className="lg:col-span-2">
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
        </div>
      </div>

      {/* Despesas Recentes (cards) */}
      <WeddingFinancesRecentExpenses
        expenses={recentExpensesItems}
        onAddExpense={() => setCreateDialogOpen(true)}
      />

      {/* Todas as Despesas (tabela com ações) */}
      <div>
        <WeddingExpensesTable
          expenses={expenses}
          weddingUuid={weddingUuid}
          onExpenseUpdated={() => {
            queryClient.invalidateQueries({
              queryKey: getFinancesExpensesListQueryKey({
                wedding_id: weddingUuid,
              }),
            });
            queryClient.invalidateQueries({
              queryKey: getFinancesExpensesListQueryKey({
                wedding_id: weddingUuid,
                limit: 5,
              }),
            });
            queryClient.invalidateQueries({
              queryKey: getFinancesBudgetsForWeddingQueryKey(weddingUuid),
            });
            queryClient.invalidateQueries({
              queryKey: getFinancesCategoriesListQueryKey({
                wedding_id: weddingUuid,
              }),
            });
          }}
        />
      </div>

      <Suspense fallback={null}>
        <CreateExpenseDialog
          weddingUuid={weddingUuid}
          open={createDialogOpen}
          onOpenChange={setCreateDialogOpen}
          onSuccess={handleExpenseCreated}
        />
      </Suspense>
    </div>
  );
}
