"use client";

import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";
import { useWeddingBudget } from "../hooks/useWeddingBudget";
import { WeddingFinancesSummaryCards } from "./WeddingFinancesSummaryCards";
import { WeddingFinancesDistributionChart } from "./WeddingFinancesDistributionChart";
import { WeddingFinancesGroupsSummary } from "./WeddingFinancesGroupsSummary";
import { WeddingFinancesRecentExpenses } from "./WeddingFinancesRecentExpenses";

interface WeddingFinancesViewProps {
  weddingUuid: string;
}

export function WeddingFinancesView({ weddingUuid }: WeddingFinancesViewProps) {
  const {
    categories,
    isLoading: isBudgetLoading,
    totalEstimated,
    totalSpent,
  } = useWeddingBudget(weddingUuid);

  const { data: expensesResponse, isLoading: isExpensesLoading } =
    useFinancesExpensesList({ wedding_id: weddingUuid, limit: 20 });

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
          <WeddingFinancesDistributionChart categories={categories} />
        </div>

        {/* Categorias e Alocação */}
        <div className="lg:col-span-2">
          <WeddingFinancesGroupsSummary categories={categories} />
        </div>
      </div>

      {/* Tabela de Despesas Recentes */}
      <WeddingFinancesRecentExpenses expenses={expenses} />
    </div>
  );
}
