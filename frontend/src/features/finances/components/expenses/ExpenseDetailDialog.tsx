import { useState } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";

import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import {
  useFinancesInstallmentsList,
  useFinancesInstallmentsMarkAsPaid,
  useFinancesInstallmentsUnmarkAsPaid,
  useFinancesExpensesRead,
  getFinancesInstallmentsListQueryKey,
  getFinancesExpensesReadQueryKey,
} from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR } from "@/lib/formatters";
import { getApiErrorInfo } from "@/api/error-utils";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
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

interface ExpenseDetailDialogProps {
  expense: ExpenseOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExpenseDetailDialog({
  expense,
  open,
  onOpenChange,
}: ExpenseDetailDialogProps) {
  const queryClient = useQueryClient();
  const [payingUuid, setPayingUuid] = useState<string | null>(null);
  const [showRedistribute, setShowRedistribute] = useState(false);

  const { data: liveExpenseResponse } = useFinancesExpensesRead(expense.uuid);
  const liveExpense = liveExpenseResponse?.data ?? expense;

  const { data: installmentsResponse, isLoading: isLoadingInstallments } =
    useFinancesInstallmentsList({ expense_id: liveExpense.uuid });

  const markAsPaidMutation = useFinancesInstallmentsMarkAsPaid();
  const unmarkAsPaidMutation = useFinancesInstallmentsUnmarkAsPaid();

  const installments = installmentsResponse?.data?.items || [];

  const paidCount = liveExpense.paid_installments_count ?? 0;
  const totalCount = liveExpense.installments_count ?? 0;
  const totalPaid = Number(liveExpense.total_paid ?? 0);
  const actualAmount = Number(liveExpense.actual_amount ?? 0);
  const progress =
    actualAmount > 0
      ? Math.min(100, Math.round((totalPaid / actualAmount) * 100))
      : 0;

  const hasAnyPaid = paidCount > 0;

  const togglePayment = async (uuid: string, isPaid: boolean) => {
    setPayingUuid(uuid);
    try {
      if (isPaid) {
        await unmarkAsPaidMutation.mutateAsync({ uuid });
        toast.success("Parcela desmarcada como paga.");
      } else {
        await markAsPaidMutation.mutateAsync({ uuid });
        toast.success("Parcela marcada como paga!");
      }
      queryClient.invalidateQueries({
        queryKey: getFinancesInstallmentsListQueryKey({ expense_id: liveExpense.uuid }),
      });
      queryClient.invalidateQueries({
        queryKey: getFinancesExpensesReadQueryKey(liveExpense.uuid),
      });
    } catch (error) {
      const action = isPaid ? "desmarcar" : "marcar";
      const { message } = getApiErrorInfo(error, `Erro ao ${action} parcela.`);
      toast.error(message);
    } finally {
      setPayingUuid(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[85vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center justify-between pr-8">
            <span className="truncate">
              {liveExpense.name || liveExpense.description || "N/A"}
            </span>
            <Badge
              variant={
                statusVariant[liveExpense.status ?? "PENDING"] ?? "outline"
              }
            >
              {statusLabel[liveExpense.status ?? "PENDING"] ?? liveExpense.status}
            </Badge>
          </DialogTitle>
          <DialogDescription asChild>
            <div className="space-y-1 pt-1">
              <p className="text-sm">
                Categoria:{" "}
                <span className="font-medium text-foreground">
                  {liveExpense.category_name ||
                    liveExpense.category.substring(0, 8)}
                </span>
              </p>
              {liveExpense.contract_description ? (
                <p className="text-sm">
                  Contrato:{" "}
                  <span className="font-medium text-foreground">
                    {liveExpense.contract_description}
                  </span>
                </p>
              ) : null}
              {liveExpense.description ? (
                <p className="text-sm text-muted-foreground pt-1">
                  {liveExpense.description}
                </p>
              ) : null}
            </div>
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4">
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
                  onClick={() => setShowRedistribute(!showRedistribute)}
                >
                  <RefreshCw className="size-3" />
                  Remanejar
                </Button>
              )}
            </div>

            {showRedistribute && (
              <ExpenseRedistributeForm
                expenseUuid={liveExpense.uuid}
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
                        onTogglePayment={togglePayment}
                      />
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );
}
