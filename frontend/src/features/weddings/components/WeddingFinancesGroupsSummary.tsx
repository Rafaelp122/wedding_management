"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatCurrencyBR, parseDecimal } from "@/features/shared/utils/formatters";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

interface WeddingFinancesGroupsSummaryProps {
  categories: BudgetCategoryOut[];
}

export function WeddingFinancesGroupsSummary({
  categories,
}: WeddingFinancesGroupsSummaryProps) {
  const formatCurrency = (value: number) => `R$ ${formatCurrencyBR(value)}`;

  return (
    <Card className="border-none shadow-sm">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-bold">Resumo por Grupo</CardTitle>
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
  );
}
