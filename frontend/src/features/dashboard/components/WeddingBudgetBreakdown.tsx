import { PiggyBank, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WeddingDashboardCategoryOut } from "@/api/generated/v1/models/weddingDashboardCategoryOut";

interface WeddingBudgetBreakdownProps {
  categories: WeddingDashboardCategoryOut[];
  isLoading?: boolean;
}

const formatCurrency = (value: number | string) =>
  new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL",
    maximumFractionDigits: 0,
  }).format(Number(value));

function CategoryBar({ category }: { category: WeddingDashboardCategoryOut }) {
  const pct = Math.min(category.percentage, 100);
  const isOver = category.percentage > 100;
  const isDanger = category.percentage >= 90;
  const isWarning = category.percentage >= 70 && category.percentage < 90;

  const barColor = isOver || isDanger
    ? "bg-destructive"
    : isWarning
      ? "bg-amber-500"
      : "bg-aura-500";

  const textColor = isOver || isDanger
    ? "text-destructive"
    : isWarning
      ? "text-amber-600 dark:text-amber-400"
      : "text-zinc-900 dark:text-zinc-100";

  const TrendIcon = isOver
    ? TrendingUp
    : isDanger
      ? TrendingUp
      : isWarning
        ? Minus
        : TrendingDown;

  const trendColor = isOver || isDanger
    ? "text-destructive"
    : isWarning
      ? "text-amber-500"
      : "text-success";

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <div className="flex items-center gap-1.5 min-w-0">
          <TrendIcon className={`w-3.5 h-3.5 shrink-0 ${trendColor}`} />
          <span className="font-medium text-zinc-800 dark:text-zinc-200 truncate">
            {category.name}
          </span>
        </div>
        <div className="flex items-center gap-3 shrink-0 ml-2 text-xs">
          <span className="text-zinc-500 dark:text-zinc-400">
            {formatCurrency(category.spent)} / {formatCurrency(category.allocated)}
          </span>
          <span className={`font-bold tabular-nums w-10 text-right ${textColor}`}>
            {isOver ? `+${(category.percentage - 100).toFixed(0)}%` : `${category.percentage.toFixed(0)}%`}
          </span>
        </div>
      </div>
      <div className="w-full bg-zinc-100 dark:bg-zinc-800 rounded-full h-1.5 overflow-hidden">
        <div
          className={`h-1.5 rounded-full transition-all duration-700 ${barColor}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

export function WeddingBudgetBreakdown({
  categories,
  isLoading,
}: WeddingBudgetBreakdownProps) {
  if (isLoading) {
    return (
      <Card className="bg-card shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full">
        <CardHeader className="pb-4 border-b border-zinc-100 dark:border-zinc-800/50">
          <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
            <PiggyBank className="w-4 h-4 text-aura-500" />
            Orçamento por Categoria
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 space-y-5 flex-1 overflow-y-auto">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="space-y-1.5 animate-pulse">
              <div className="flex justify-between">
                <div className="h-4 w-32 bg-zinc-200 dark:bg-zinc-700 rounded" />
                <div className="h-4 w-24 bg-zinc-200 dark:bg-zinc-700 rounded" />
              </div>
              <div className="h-1.5 w-full bg-zinc-100 dark:bg-zinc-800 rounded-full" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (!categories || categories.length === 0) {
    return (
      <Card className="bg-card shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full">
        <CardHeader className="pb-4 border-b border-zinc-100 dark:border-zinc-800/50">
          <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
            <PiggyBank className="w-4 h-4 text-aura-500" />
            Orçamento por Categoria
          </CardTitle>
        </CardHeader>
        <CardContent className="p-6 flex flex-col items-center justify-center text-center py-10 flex-1">
          <PiggyBank className="w-8 h-8 text-zinc-300 dark:text-zinc-600 mb-3" />
          <p className="text-sm text-zinc-500 dark:text-zinc-400">
            Nenhuma categoria de orçamento cadastrada.
          </p>
        </CardContent>
      </Card>
    );
  }

  // Sort by percentage desc to show most spent categories first
  const sorted = [...categories].sort((a, b) => b.percentage - a.percentage);

  const totalAllocated = categories.reduce(
    (sum, c) => sum + Number(c.allocated),
    0,
  );
  const totalSpent = categories.reduce(
    (sum, c) => sum + Number(c.spent),
    0,
  );
  const totalPct = totalAllocated > 0
    ? Math.round((totalSpent / totalAllocated) * 100)
    : 0;

  return (
    <Card className="bg-card shadow-soft border-zinc-200 dark:border-zinc-800 flex flex-col h-full">
      <CardHeader className="pb-4 border-b border-zinc-100 dark:border-zinc-800/50">
        <div className="flex items-center justify-between">
          <CardTitle className="text-base font-semibold text-zinc-900 dark:text-white flex items-center gap-2">
            <PiggyBank className="w-4 h-4 text-aura-500" />
            Orçamento por Categoria
          </CardTitle>
          <div className="flex items-center gap-1.5 text-xs font-medium text-zinc-500 dark:text-zinc-400">
            <span>{formatCurrency(totalSpent)}</span>
            <span>/</span>
            <span className="text-zinc-700 dark:text-zinc-300">{formatCurrency(totalAllocated)}</span>
            <span
              className={`ml-1 font-bold ${
                totalPct >= 90
                  ? "text-destructive"
                  : totalPct >= 70
                    ? "text-amber-500"
                    : "text-success"
              }`}
            >
              ({totalPct}%)
            </span>
          </div>
        </div>
      </CardHeader>
      <CardContent className="p-6 space-y-5 flex-1 overflow-y-auto">
        {sorted.map((category) => (
          <CategoryBar key={category.name} category={category} />
        ))}
      </CardContent>
    </Card>
  );
}
