"use client";

import React from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import {
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle2,
} from "lucide-react";

import { useWeddingBudget } from "../hooks/useWeddingBudget";
import { useWeddingExpenses } from "../hooks/useWeddingExpenses";
import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

import { WeddingBudgetCategoriesCard } from "./WeddingBudgetCategoriesCard";

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

  const { expenses, isLoading: isExpensesLoading } = useWeddingExpenses(weddingUuid);

  const { data: installmentsResponse, isLoading: isInstallmentsLoading } = useFinancesInstallmentsList({
    limit: 5,
  });

  const formatCurrency = (value: number) => {
    return `R$ ${formatCurrencyBR(value)}`;
  };

  // Filtramos apenas categorias que tenham orçamento alocado ou gasto real
  const activeCategories = categories.filter(
    (cat) => Number(cat.allocated_budget) > 0 || Number(cat.total_spent || 0) > 0
  );

  const hasChartData = activeCategories.length > 0;

  const chartData = activeCategories.map((cat) => ({
    name: cat.name,
    Orçado: Number(cat.allocated_budget),
    Realizado: Number(cat.total_spent || 0),
  }));

  const installments = installmentsResponse?.data?.items?.filter(i => i.wedding === weddingUuid) || [];

  if (isBudgetLoading || isExpensesLoading || isInstallmentsLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Skeleton className="h-[400px] w-full" />
      </div>
    );
  }

  const availableBalance = totalEstimated - totalSpent;

  return (
    <div className="space-y-6">
      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Orçamento Estimado (Teto Global)</p>
          <p className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mt-1 tabular-nums">
            {formatCurrency(totalEstimated)}
          </p>
        </div>
        <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Total Gasto (Realizado)</p>
          <div className="flex items-baseline gap-2 mt-1">
            <p className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 tabular-nums">
              {formatCurrency(totalSpent)}
            </p>
            {totalSpent <= totalEstimated ? (
              <span className="text-xs font-medium text-green-600 flex items-center tabular-nums">
                <ArrowDownRight className="w-3 h-3 mr-0.5" />
                Dentro do limite
              </span>
            ) : (
              <span className="text-xs font-medium text-red-600 flex items-center tabular-nums">
                <ArrowUpRight className="w-3 h-3 mr-0.5" />
                Acima do limite
              </span>
            )}
          </div>
        </div>
        <div className="bg-white dark:bg-zinc-900 p-5 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm">
          <p className="text-sm font-medium text-zinc-500">Saldo Disponível</p>
          <p className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50 mt-1 tabular-nums">
            {formatCurrency(availableBalance)}
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Column: Chart */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm min-h-[400px] flex flex-col">
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-50 mb-6">
            Planejamento vs. Execução por Categoria
          </h3>

          {hasChartData ? (
            <div className="h-[300px] w-full flex-1">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e4e4e7" />
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: "#71717a" }}
                    dy={10}
                  />
                  <YAxis
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 10, fill: "#71717a" }}
                    tickFormatter={(value) => `R$ ${value / 1000}k`}
                  />
                  <Tooltip
                    cursor={{ fill: "#f4f4f5" }}
                    contentStyle={{
                      borderRadius: "8px",
                      border: "1px solid #e4e4e7",
                      boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                    }}
                    formatter={(value: number) => formatCurrency(value)}
                  />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: "12px", paddingTop: "20px" }} />
                  <Bar dataKey="Orçado" fill="#e4e4e7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Realizado" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground border-2 border-dashed rounded-lg bg-zinc-50/50 dark:bg-zinc-950/20">
              <BarChartIcon className="size-10 mb-4 opacity-20" />
              <p className="text-sm font-medium">Gráfico de Comparação</p>
              <p className="text-xs mt-1 text-center max-w-[250px]">
                O gráfico aparecerá aqui assim que você definir o teto orçamentário para as categorias ou registrar a primeira despesa.
              </p>
            </div>
          )}
        </div>

        {/* Side Column: Upcoming Installments */}
        <div className="bg-white dark:bg-zinc-900 p-6 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">Próximos Vencimentos</h3>
            <button className="text-sm font-medium text-primary hover:underline">Ver todas</button>
          </div>
          <div className="space-y-4 flex-1">
            {installments.length > 0 ? (
              installments.map((installment) => (
                <div
                  key={installment.uuid}
                  className="flex items-start justify-between p-3 rounded-lg hover:bg-zinc-50 dark:hover:bg-zinc-800 transition-colors border border-transparent hover:border-zinc-100 dark:border-zinc-800/50"
                >
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center flex-shrink-0">
                      <Clock className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                        Parcela #{installment.installment_number}
                      </p>
                      <p className="text-xs text-zinc-500">Vencimento: {installment.due_date}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50 tabular-nums">
                      {formatCurrency(Number(installment.amount))}
                    </p>
                  </div>
                </div>
              ))
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center py-8 text-muted-foreground">
                <Clock className="size-8 mb-2 opacity-20" />
                <p className="text-xs">Sem parcelas pendentes.</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Alocação de Teto por Categoria (Fundamental para o planejamento) */}
      <WeddingBudgetCategoriesCard categories={activeCategories} />

      {/* Bottom: Expenses List (Bank Statement Style) */}
      <div className="bg-white dark:bg-zinc-900 rounded-xl border border-zinc-200 dark:border-zinc-800 shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-zinc-200 dark:border-zinc-800 flex items-center justify-between">
          <h3 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">Extrato de Despesas</h3>
          <Button size="sm" variant="outline" className="gap-2">
            <Plus className="size-4" />
            Adicionar Despesa
          </Button>
        </div>
        <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {expenses.length > 0 ? (
            expenses.slice(0, 10).map((expense) => {
              const date = new Date(expense.date);
              const formattedDay = date.getDate().toString().padStart(2, "0");
              const formattedMonth = date.toLocaleString("pt-BR", { month: "short" }).toUpperCase();

              return (
                <div
                  key={expense.uuid}
                  className="px-6 py-4 flex items-center justify-between hover:bg-zinc-50/50 dark:hover:bg-zinc-800/50 transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-12 text-xs font-medium text-zinc-400 dark:text-zinc-500 text-center">
                      {formattedDay}
                      <br />
                      {formattedMonth}
                    </div>
                    <div className="w-2 h-2 rounded-full bg-green-500" />
                    <div>
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">{expense.description}</p>
                      <p className="text-xs text-zinc-500">{expense.category_name}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 tabular-nums">
                        {formatCurrency(Number(expense.amount))}
                      </p>
                      <p className="text-xs text-zinc-500 flex items-center justify-end gap-1">
                        <CheckCircle2 className="w-3 h-3 text-green-500" /> Pago
                      </p>
                    </div>
                  </div>
                </div>
              );
            })
          ) : (
            <p className="px-6 py-12 text-sm text-muted-foreground text-center">Nenhuma despesa registrada no sistema.</p>
          )}
        </div>
      </div>
    </div>
  );
}

// Novos ícones e componentes necessários
import { BarChart as BarChartIcon, Plus } from "lucide-react";
