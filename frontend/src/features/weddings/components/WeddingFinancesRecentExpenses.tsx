"use client";

import { DollarSign, CheckCircle2, Plus } from "lucide-react";
import {
  Card,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import type { ExpenseOut } from "@/api/generated/v1/models";

interface WeddingFinancesRecentExpensesProps {
  expenses: ExpenseOut[];
}

export function WeddingFinancesRecentExpenses({
  expenses,
}: WeddingFinancesRecentExpensesProps) {
  const formatCurrency = (value: number) => `R$ ${formatCurrencyBR(value)}`;

  return (
    <Card className="border-none shadow-sm overflow-hidden">
      <div className="px-6 py-5 border-b border-zinc-100 dark:border-zinc-800 flex items-center justify-between">
        <div>
          <CardTitle className="text-lg font-bold">Despesas Recentes</CardTitle>
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
            return (
              <div
                key={expense.uuid}
                className="px-6 py-4 flex items-center justify-between hover:bg-zinc-50/50 dark:hover:bg-zinc-800/50 transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center">
                    <DollarSign className="w-5 h-5 text-zinc-400" />
                  </div>
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <div>
                    <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                      {expense.description}
                    </p>
                    <p className="text-xs text-zinc-500">{expense.category}</p>
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
  );
}
