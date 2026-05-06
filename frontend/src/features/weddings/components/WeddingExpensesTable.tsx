import { useState } from "react";
import { MoreHorizontal } from "lucide-react";
import type { ExpenseOut } from "@/api/generated/v1/models";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
import { EditExpenseDialog } from "./EditExpenseDialog";
import { DeleteExpenseDialog } from "./DeleteExpenseDialog";
import { ExpenseDetailDialog } from "./ExpenseDetailDialog";

interface WeddingExpensesTableProps {
  expenses: ExpenseOut[];
  weddingUuid: string;
  onExpenseUpdated: () => void;
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

export function WeddingExpensesTable({
  expenses,
  weddingUuid,
  onExpenseUpdated,
}: WeddingExpensesTableProps) {
  const [editingExpense, setEditingExpense] = useState<ExpenseOut | null>(null);
  const [deletingExpense, setDeletingExpense] = useState<ExpenseOut | null>(null);
  const [detailExpense, setDetailExpense] = useState<ExpenseOut | null>(null);

  if (expenses.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhuma despesa registrada para este evento.</p>
      </div>
    );
  }

  return (
    <>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Nome</TableHead>
              <TableHead>Categoria</TableHead>
              <TableHead className="text-right">Valor Est.</TableHead>
              <TableHead className="text-right">Valor Real.</TableHead>
              <TableHead>Parcelas</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="w-10" />
            </TableRow>
          </TableHeader>
          <TableBody>
            {expenses.map((expense) => {
              const status = expense.status ?? "PENDING";
              const paidCount = expense.paid_installments_count ?? 0;
              const totalCount = expense.installments_count ?? 0;

              return (
                <TableRow
                  key={expense.uuid}
                  tabIndex={0}
                  role="button"
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => setDetailExpense(expense)}
                  onKeyDown={(e) => {
                    if (e.target !== e.currentTarget) return;
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setDetailExpense(expense);
                    }
                  }}
                >
                  <TableCell className="font-medium text-sm max-w-40 truncate">
                    {expense.name || expense.description || "N/A"}
                  </TableCell>
                  <TableCell className="text-xs text-muted-foreground">
                    {expense.category_name || expense.category.substring(0, 8)}
                  </TableCell>
                  <TableCell className="text-right text-xs">
                    R$ {formatCurrencyBR(Number(expense.estimated_amount))}
                  </TableCell>
                  <TableCell className="text-right font-medium text-sm">
                    R$ {formatCurrencyBR(Number(expense.actual_amount))}
                  </TableCell>
                  <TableCell>
                    <span className="text-xs text-muted-foreground">
                      {paidCount}/{totalCount}
                    </span>
                  </TableCell>
                  <TableCell>
                    <Badge
                      variant={statusVariant[status] ?? "outline"}
                      className="text-[10px] h-4"
                    >
                      {statusLabel[status] ?? status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-7 w-7 p-0"
                          aria-label="Ações da despesa"
                          onClick={(e) => e.stopPropagation()}
                        >
                          <MoreHorizontal className="size-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem
                          onClick={(e) => {
                            e.stopPropagation();
                            setEditingExpense(expense);
                          }}
                        >
                          Editar
                        </DropdownMenuItem>
                        <DropdownMenuItem
                          className="text-destructive"
                          onClick={(e) => {
                            e.stopPropagation();
                            setDeletingExpense(expense);
                          }}
                        >
                          Excluir
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </div>

      {editingExpense && (
        <EditExpenseDialog
          expense={editingExpense}
          weddingUuid={weddingUuid}
          open={!!editingExpense}
          onOpenChange={(open) => {
            if (!open) setEditingExpense(null);
          }}
          onSuccess={() => {
            setEditingExpense(null);
            onExpenseUpdated();
          }}
        />
      )}

      {deletingExpense && (
        <DeleteExpenseDialog
          expense={deletingExpense}
          open={!!deletingExpense}
          onOpenChange={(open) => {
            if (!open) setDeletingExpense(null);
          }}
          onSuccess={() => {
            setDeletingExpense(null);
            onExpenseUpdated();
          }}
        />
      )}

      {detailExpense && (
        <ExpenseDetailDialog
          expense={detailExpense}
          open={!!detailExpense}
          onOpenChange={(open) => {
            if (!open) setDetailExpense(null);
          }}
        />
      )}
    </>
  );
}
