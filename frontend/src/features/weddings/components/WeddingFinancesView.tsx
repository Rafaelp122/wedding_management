"use client";

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
  DollarSign,
  TrendingDown,
  CheckCircle2,
  BarChart as BarChartIcon,
  Plus,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";
import { useWeddingBudget } from "../hooks/useWeddingBudget";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";

interface WeddingFinancesViewProps {
  weddingUuid: string;
}

export function WeddingFinancesView({ weddingUuid }: WeddingFinancesViewProps) {
  const parseDecimal = (value?: string | null) => {
    if (!value) {
      return 0;
    }

    const parsed = Number.parseFloat(value);
    return Number.isFinite(parsed) ? parsed : 0;
  };

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

  const formatCurrency = (value: number) => formatCurrencyBR(value);

  const budgetUsage =
    totalEstimated > 0 ? Math.round((totalSpent / totalEstimated) * 100) : 0;

  const chartData = categories.map((cat) => ({
    name: cat.name,
    estimado: parseDecimal(cat.allocated_budget),
    real: parseDecimal(cat.total_spent),
  }));

  const expenses = expensesResponse?.data?.items || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Resumo Financeiro */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="border-none shadow-sm bg-violet-50/50 dark:bg-violet-900/10">
          <CardHeader className="pb-2">
            <CardDescription className="text-violet-600 dark:text-violet-400 font-medium">
              Orçamento Total
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
              {formatCurrency(totalEstimated)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-1 text-xs text-green-600 font-medium">
              <ArrowUpRight className="w-3 h-3" />
              <span>12% maior que a média</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm bg-emerald-50/50 dark:bg-emerald-900/10">
          <CardHeader className="pb-2">
            <CardDescription className="text-emerald-600 dark:text-emerald-400 font-medium">
              Total Gasto
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
              {formatCurrency(totalSpent)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-1 text-xs text-emerald-600 font-medium">
              <TrendingDown className="w-3 h-3" />
              <span>Dentro do planejado</span>
            </div>
          </CardContent>
        </Card>

        <Card className="border-none shadow-sm bg-zinc-50/50 dark:bg-zinc-800/50">
          <CardHeader className="pb-2">
            <CardDescription className="font-medium text-zinc-500">
              Saldo Disponível
            </CardDescription>
            <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
              {formatCurrency(totalEstimated - totalSpent)}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-medium">
                <span className="text-zinc-500">Uso do Orçamento</span>
                <span
                  className={
                    budgetUsage > 90 ? "text-red-500" : "text-violet-600"
                  }
                >
                  {budgetUsage}%
                </span>
              </div>
              <Progress value={budgetUsage} className="h-1.5" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-8">
        {/* Gráfico de Distribuição */}
        <Card className="lg:col-span-3 border-none shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg font-bold flex items-center gap-2">
              <BarChartIcon className="w-5 h-5 text-violet-500" />
              Distribuição por Categoria
            </CardTitle>
            <CardDescription>
              Comparativo entre valores estimados e gastos reais
            </CardDescription>
          </CardHeader>
          <CardContent className="h-87.5 pt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart
                data={chartData}
                margin={{ top: 0, right: 0, left: -20, bottom: 0 }}
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                  vertical={false}
                  stroke="#f0f0f0"
                />
                <XAxis
                  dataKey="name"
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#888", fontSize: 12 }}
                  dy={10}
                />
                <YAxis
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#888", fontSize: 12 }}
                />
                <Tooltip
                  cursor={{ fill: "#f8f8f8" }}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "none",
                    boxShadow: "0 4px 12px rgba(0,0,0,0.1)",
                  }}
                />
                <Legend
                  iconType="circle"
                  wrapperStyle={{ paddingTop: "20px" }}
                />
                <Bar
                  dataKey="estimado"
                  fill="#ddd6fe"
                  radius={[4, 4, 0, 0]}
                  name="Estimado"
                />
                <Bar
                  dataKey="real"
                  fill="#7c3aed"
                  radius={[4, 4, 0, 0]}
                  name="Realizado"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        {/* Categorias e Alocação */}
        <div className="lg:col-span-2 space-y-6">
          <Card className="border-none shadow-sm">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg font-bold">
                Resumo por Grupo
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-5">
              {categories.slice(0, 5).map((category) => {
                const allocatedBudget = parseDecimal(category.allocated_budget);
                const spentAmount = parseDecimal(category.total_spent);
                const percentage =
                  allocatedBudget > 0
                    ? Math.round((spentAmount / allocatedBudget) * 100)
                    : 0;

                return (
                  <div key={category.uuid} className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">
                        {category.name}
                      </span>
                      <span className="text-sm font-bold text-zinc-900 dark:text-zinc-100">
                        {formatCurrency(spentAmount)}
                      </span>
                    </div>
                    <div className="relative h-2 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="absolute top-0 left-0 h-full bg-violet-500 rounded-full transition-all duration-500"
                        style={{ width: `${Math.min(percentage, 100)}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-[10px] text-zinc-400 uppercase font-bold tracking-wider">
                      <span>{percentage}% do teto</span>
                      <span>Teto: {formatCurrency(allocatedBudget)}</span>
                    </div>
                  </div>
                );
              })}
              <Button
                variant="outline"
                className="w-full mt-2 text-xs font-bold border-zinc-200 text-zinc-600 hover:bg-zinc-50"
              >
                Ver Todas Categorias
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Tabela de Despesas Recentes */}
      <Card className="border-none shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
          <div>
            <CardTitle className="text-lg font-bold">
              Despesas Recentes
            </CardTitle>
            <CardDescription>
              Últimas movimentações financeiras do evento
            </CardDescription>
          </div>
          <Button
            size="sm"
            className="bg-violet-600 hover:bg-violet-700 text-white rounded-full px-4 text-xs font-bold gap-2"
          >
            <Plus className="w-3 h-3" />
            Adicionar Despesa
          </Button>
        </div>
        <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {expenses.length > 0 ? (
            expenses.slice(0, 10).map((expense) => {
              // ExpenseOut doesn't have a date field in the generated model, using current date as fallback
              const date = new Date();
              const formattedDay = date.getDate().toString().padStart(2, "0");
              const formattedMonth = date
                .toLocaleString("pt-BR", { month: "short" })
                .toUpperCase();

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
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                        {expense.description}
                      </p>
                      <p className="text-xs text-zinc-500">
                        {expense.category}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 tabular-nums">
                        {formatCurrency(Number(expense.actual_amount))}
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
            <div className="py-12 text-center">
              <div className="w-12 h-12 rounded-full bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center mx-auto mb-3">
                <DollarSign className="w-6 h-6 text-zinc-300" />
              </div>
              <p className="text-sm text-zinc-500 dark:text-zinc-400 font-medium">
                Nenhuma despesa registrada no sistema.
              </p>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
