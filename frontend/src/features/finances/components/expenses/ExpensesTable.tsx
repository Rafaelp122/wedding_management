import { memo } from "react";
import { MoreHorizontal } from "lucide-react";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
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
import { formatCurrencyBR } from "@/lib/formatters";

interface WeddingExpensesTableProps {
  expenses: ExpenseOut[];
  onEditExpense: (expense: ExpenseOut) => void;
  onDeleteExpense: (expense: ExpenseOut) => void;
  onDetailExpense: (expense: ExpenseOut) => void;
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

export const WeddingExpensesTable = memo(function WeddingExpensesTable({
  expenses,
  onEditExpense,
  onDeleteExpense,
  onDetailExpense,
}: WeddingExpensesTableProps) {
  if (expenses.length === 0) {
    return (
      <div className="text-center py-6 text-muted-foreground border rounded-md">
        <p className="text-sm">Nenhuma despesa registrada para este evento.</p>
      </div>
    );
  }

  return (
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
                className="hover:bg-muted/50"
              >
                <TableCell className="font-medium text-sm max-w-40 truncate p-0">
                  <Button
                    variant="link"
                    className="h-auto w-full justify-start px-4 py-3 text-sm font-medium text-foreground hover:no-underline"
                    onClick={() => onDetailExpense(expense)}
                  >
                    {expense.name || expense.description || "N/A"}
                  </Button>
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
                      >
                        <MoreHorizontal className="size-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => onEditExpense(expense)}>
                        Editar
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={() => onDeleteExpense(expense)}
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
  );
});
