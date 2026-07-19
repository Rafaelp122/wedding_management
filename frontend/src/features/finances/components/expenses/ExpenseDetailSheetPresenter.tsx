import { RefreshCw } from "lucide-react";

import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import type { InstallmentOut } from "@/api/generated/v1/models/installmentOut";
import { formatCurrencyBR } from "@/lib/formatters";
import { calculateExpenseProgress } from "@/features/finances/utils/expenseCalculations";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

import { ExpenseInstallmentRow } from "./ExpenseInstallmentRow";
import { ExpenseRedistributeForm } from "./ExpenseRedistributeForm";
import { statusVariant, statusLabel } from "./constants";

export interface ExpenseDetailSheetPresenterProps {
  expense: ExpenseOut;
  installments: InstallmentOut[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
  isLoadingInstallments: boolean;
  payingUuid: string | null;
  onTogglePayment: (uuid: string, isPaid: boolean) => Promise<void> | void;
  showRedistribute: boolean;
  onToggleRedistribute: () => void;
}

export function ExpenseDetailSheetPresenter({
  expense,
  installments,
  open,
  onOpenChange,
  isLoadingInstallments,
  payingUuid,
  onTogglePayment,
  showRedistribute,
  onToggleRedistribute,
}: ExpenseDetailSheetPresenterProps) {
  const paidCount = expense.paid_installments_count ?? 0;
  const totalCount = expense.installments_count ?? 0;
  const totalPaid = Number(expense.total_paid ?? 0);
  const actualAmount = Number(expense.actual_amount ?? 0);
  const progress = calculateExpenseProgress(expense);

  const hasAnyPaid = paidCount > 0;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="sm:max-w-[600px] h-full overflow-y-auto">
        <SheetHeader>
          <SheetTitle className="flex items-center justify-between pr-8">
            <span className="truncate">
              {expense.name || expense.description || "N/A"}
            </span>
            <Badge
              variant={
                statusVariant[expense.status ?? "PENDING"] ?? "outline"
              }
            >
              {statusLabel[expense.status ?? "PENDING"] ?? expense.status}
            </Badge>
          </SheetTitle>
          <SheetDescription asChild>
            <div className="space-y-1 pt-1">
              <p className="text-sm">
                Categoria:{" "}
                <span className="font-medium text-foreground">
                  {expense.category_name ||
                    expense.category.substring(0, 8)}
                </span>
              </p>
              {expense.contract_description ? (
                <p className="text-sm">
                  Contrato:{" "}
                  <span className="font-medium text-foreground">
                    {expense.contract_description}
                  </span>
                </p>
              ) : null}
              {expense.description ? (
                <p className="text-sm text-muted-foreground pt-1">
                  {expense.description}
                </p>
              ) : null}
            </div>
          </SheetDescription>
        </SheetHeader>

        <div className="space-y-4 mt-4">
          <div className="rounded-lg border bg-muted/30 p-4 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">
                {paidCount}/{totalCount} marcadas como pagas
              </span>
              <span className="font-medium">
                {formatCurrencyBR(totalPaid)} de {formatCurrencyBR(actualAmount)}
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold">Parcelas</h4>
              {!hasAnyPaid && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs gap-1"
                  onClick={onToggleRedistribute}
                >
                  <RefreshCw className="size-3" />
                  Remanejar
                </Button>
              )}
            </div>

            {showRedistribute && (
              <ExpenseRedistributeForm
                expenseUuid={expense.uuid}
                currentCount={totalCount}
                firstExistingDate={
                  installments[0]?.due_date.slice(0, 10) ?? null
                }
              />
            )}

            {isLoadingInstallments ? (
              <Skeleton className="h-32 w-full" />
            ) : installments.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Nenhuma parcela encontrada.
              </p>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-12">#</TableHead>
                      <TableHead>Valor</TableHead>
                      <TableHead>Vencimento</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="w-12" />
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {installments.map((inst) => (
                      <ExpenseInstallmentRow
                        key={inst.uuid}
                        installment={inst}
                        isPaying={payingUuid === inst.uuid}
                        onTogglePayment={onTogglePayment}
                      />
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
