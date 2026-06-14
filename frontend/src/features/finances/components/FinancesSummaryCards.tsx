import { ArrowUpRight, ArrowDownRight, TrendingDown, TrendingUp, AlertTriangle } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatCurrencyBRCompact } from "@/lib/formatters";
import { useFinancesBudgetsList } from "@/api/generated/v1/endpoints/finances/finances";

interface WeddingFinancesSummaryCardsProps {
  totalEstimated: number;
  totalSpent: number;
}

export function WeddingFinancesSummaryCards({
  totalEstimated,
  totalSpent,
}: WeddingFinancesSummaryCardsProps) {
  const budgetUsage =
    totalEstimated > 0 ? Math.round((totalSpent / totalEstimated) * 100) : 0;
  const clampedBudgetUsage = Math.min(100, Math.max(0, budgetUsage));

  const { data: budgetsListResponse, isLoading: budgetsLoading } = useFinancesBudgetsList();
  const budgets = budgetsListResponse?.data?.items || [];
  const validBudgets = budgets.filter((b) => Number(b.total_estimated) > 0);
  const hasEnoughData = validBudgets.length >= 2;

  let averageBudget = 0;
  let diffPercentage = 0;
  let isBudgetGreater = false;
  let isBudgetEqual = false;

  if (hasEnoughData) {
    const totalOfBudgets = validBudgets.reduce(
      (sum, b) => sum + Number(b.total_estimated),
      0
    );
    averageBudget = totalOfBudgets / validBudgets.length;
    if (averageBudget > 0) {
      if (totalEstimated > averageBudget) {
        diffPercentage = Math.round(((totalEstimated - averageBudget) / averageBudget) * 100);
        isBudgetGreater = true;
      } else if (totalEstimated < averageBudget) {
        diffPercentage = Math.round(((averageBudget - totalEstimated) / averageBudget) * 100);
        isBudgetGreater = false;
      } else {
        isBudgetEqual = true;
      }
    }
  }

  // Definição do status dinâmico do Total Gasto
  let spentStatusText = "Dentro do planejado";
  let spentStatusColorClass = "text-emerald-600 dark:text-emerald-400";
  let SpentStatusIcon = TrendingDown;

  if (totalEstimated === 0) {
    if (totalSpent > 0) {
      spentStatusText = "Acima do orçamento";
      spentStatusColorClass = "text-red-600 dark:text-red-400";
      SpentStatusIcon = TrendingUp;
    } else {
      spentStatusText = "Dentro do planejado";
      spentStatusColorClass = "text-emerald-600 dark:text-emerald-400";
      SpentStatusIcon = TrendingDown;
    }
  } else if (budgetUsage > 100) {
    spentStatusText = "Acima do orçamento";
    spentStatusColorClass = "text-red-600 dark:text-red-400";
    SpentStatusIcon = TrendingUp;
  } else if (budgetUsage >= 90) {
    spentStatusText = `Atenção: ${budgetUsage}% utilizado`;
    spentStatusColorClass = "text-amber-600 dark:text-amber-500";
    SpentStatusIcon = AlertTriangle;
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Card className="border-none shadow-sm bg-violet-50/50 dark:bg-violet-900/10">
        <CardHeader className="pb-2">
          <CardDescription className="text-violet-600 dark:text-violet-400 font-medium">
            Orçamento Total
          </CardDescription>
          <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            {formatCurrencyBRCompact(totalEstimated)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          {budgetsLoading ? (
            <div className="flex items-center gap-1 text-xs">
              <div className="w-3 h-3 rounded-full bg-muted animate-pulse" />
              <div className="h-3 w-36 bg-muted rounded animate-pulse" />
            </div>
          ) : hasEnoughData ? (
            <div
              className={`flex items-center gap-1 text-xs font-medium ${
                isBudgetEqual
                  ? "text-zinc-500 dark:text-zinc-400"
                  : isBudgetGreater
                  ? "text-green-600 dark:text-green-400"
                  : "text-blue-600 dark:text-blue-400"
              }`}
            >
              {isBudgetEqual ? (
                <TrendingDown className="w-3 h-3" />
              ) : isBudgetGreater ? (
                <ArrowUpRight className="w-3 h-3" />
              ) : (
                <ArrowDownRight className="w-3 h-3" />
              )}
              <span>
                {isBudgetEqual
                  ? "Na média dos casamentos"
                  : `${diffPercentage}% ${isBudgetGreater ? "maior" : "menor"} que a média`}
              </span>
            </div>
          ) : null}
        </CardContent>
      </Card>

      <Card className="border-none shadow-sm bg-emerald-50/50 dark:bg-emerald-900/10">
        <CardHeader className="pb-2">
          <CardDescription className="text-emerald-600 dark:text-emerald-400 font-medium">
            Total Gasto
          </CardDescription>
          <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            {formatCurrencyBRCompact(totalSpent)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className={`flex items-center gap-1 text-xs font-medium ${spentStatusColorClass}`}>
            <SpentStatusIcon className="w-3 h-3" />
            <span>{spentStatusText}</span>
          </div>
        </CardContent>
      </Card>

      <Card className="border-none shadow-sm bg-zinc-50/50 dark:bg-zinc-800/50">
        <CardHeader className="pb-2">
          <CardDescription className="font-medium text-zinc-500">
            Saldo Disponível
          </CardDescription>
          <CardTitle className="text-3xl font-bold text-zinc-900 dark:text-zinc-50">
            {formatCurrencyBRCompact(totalEstimated - totalSpent)}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <div className="flex justify-between text-xs font-medium">
              <span className="text-zinc-500">Uso do Orçamento</span>
              <span
                className={budgetUsage > 90 ? "text-red-500" : "text-violet-600"}
              >
                {budgetUsage}%
              </span>
            </div>
            <Progress value={clampedBudgetUsage} className="h-1.5" />
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
