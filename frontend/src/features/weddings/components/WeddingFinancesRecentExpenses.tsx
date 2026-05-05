"use client";

import { useState } from "react";
import { DollarSign, Plus } from "lucide-react";
import {
  Card,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import type { ExpenseOut } from "@/api/generated/v1/models";
import { ExpenseDetailDialog } from "./ExpenseDetailDialog";

interface WeddingFinancesRecentExpensesProps {
  expenses: ExpenseOut[];
  onAddExpense?: () => void;
}

const statusVariant: Record<string, "default" | "destructive" | "outline"> = {
  SETTLED: "default",
  PARTIALLY_PAID: "outline",
  PENDING: "outline",
};

const statusLabel: Record<string, string> = {
  SETTLED: "Quitada",
  PARTIALLY_PAID: "Parcial",
  PENDING: "Pendente",
};

export function WeddingFinancesRecentExpenses({
  expenses,
  onAddExpense,
}: WeddingFinancesRecentExpensesProps) {
  const [selectedExpense, setSelectedExpense] = useState<ExpenseOut | null>(null);
  const formatCurrency = (value: number) => `R$ ${formatCurrencyBR(value)}`;

  return (
    <>
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
            onClick={onAddExpense}
            className="bg-violet-600 hover:bg-violet-700 text-white rounded-full px-4 text-xs font-bold gap-2"
          >
            <Plus className="w-3 h-3" />
            Adicionar Despesa
          </Button>
        </div>
        <div className="divide-y divide-zinc-100 dark:divide-zinc-800">
          {expenses.length > 0 ? (
            expenses.slice(0, 10).map((expense) => {
              const count = expense.installments_count ?? 0;
              const status = expense.status ?? "PENDING";

              return (
                <div
                  key={expense.uuid}
                  tabIndex={0}
                  role="button"
                  className="px-6 py-4 flex items-center justify-between hover:bg-zinc-50/50 dark:hover:bg-zinc-800/50 transition-colors cursor-pointer"
                  onClick={() => setSelectedExpense(expense)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelectedExpense(expense);
                    }
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-zinc-50 dark:bg-zinc-800 flex items-center justify-center">
                      <DollarSign className="w-5 h-5 text-zinc-400" />
                    </div>
                  <div>
                    <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50">
                      {expense.name || expense.description || "N/A"}
                    </p>
                    <p className="text-xs text-zinc-500">
                      {expense.category_name || expense.category.substring(0, 8)}
                    </p>
                  </div>
                  </div>
                  <div className="flex items-center gap-6">
                    <div className="text-right">
                      <p className="text-sm font-medium text-zinc-900 dark:text-zinc-50 tabular-nums">
                        {formatCurrency(Number(expense.actual_amount))}
                      </p>
                      <div className="flex items-center justify-end gap-2">
                        {count > 0 && (
                          <span className="text-xs text-zinc-400">
                            {expense.paid_installments_count}/{count} parcelas
                          </span>
                        )}
                        <Badge
                          variant={statusVariant[status] ?? "outline"}
                          className="text-[10px] h-4"
                        >
                          {statusLabel[status] ?? status}
                        </Badge>
                      </div>
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

      {selectedExpense && (
        <ExpenseDetailDialog
          expense={selectedExpense}
          open={!!selectedExpense}
          onOpenChange={(open) => {
            if (!open) setSelectedExpense(null);
          }}
        />
      )}
    </>
  );
}
