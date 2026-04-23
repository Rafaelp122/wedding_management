"use client";

import { ArrowUpRight, TrendingDown } from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";

interface WeddingFinancesSummaryCardsProps {
  totalEstimated: number;
  totalSpent: number;
}

export function WeddingFinancesSummaryCards({
  totalEstimated,
  totalSpent,
}: WeddingFinancesSummaryCardsProps) {
  const formatCurrency = (value: number) => `R$ ${formatCurrencyBR(value)}`;

  const budgetUsage =
    totalEstimated > 0 ? Math.round((totalSpent / totalEstimated) * 100) : 0;
  const clampedBudgetUsage = Math.min(100, Math.max(0, budgetUsage));

  return (
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
