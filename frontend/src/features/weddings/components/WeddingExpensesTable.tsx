import type { ExpenseOut } from "@/api/generated/v1/models";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";

interface WeddingExpensesTableProps {
  expenses: ExpenseOut[];
}

export function WeddingExpensesTable({ expenses }: WeddingExpensesTableProps) {
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
            <TableHead>Categoria (Ref)</TableHead>
            <TableHead>Descrição</TableHead>
            <TableHead className="text-right">Valor Estimado</TableHead>
            <TableHead className="text-right">Valor Realizado</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {expenses.map((expense) => (
            <TableRow key={expense.uuid}>
              <TableCell className="font-medium text-xs text-muted-foreground uppercase">
                {expense.category.substring(0, 8)}
              </TableCell>
              <TableCell className="max-w-50 truncate" title={expense.description}>
                {expense.description || "N/A"}
              </TableCell>
              <TableCell className="text-right">
                R$ {formatCurrencyBR(Number(expense.estimated_amount))}
              </TableCell>
              <TableCell className="text-right font-medium">
                R$ {formatCurrencyBR(Number(expense.actual_amount))}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
