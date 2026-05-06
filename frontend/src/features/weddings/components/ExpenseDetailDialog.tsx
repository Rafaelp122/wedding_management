import { useState } from "react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { Check, AlertTriangle, Clock, RefreshCw, X } from "lucide-react";

import type { ExpenseOut } from "@/api/generated/v1/models";
import {
  useFinancesInstallmentsList,
  useFinancesInstallmentsMarkAsPaid,
  useFinancesInstallmentsUnmarkAsPaid,
  useFinancesExpensesUpdate,
  useFinancesExpensesRead,
} from "@/api/generated/v1/endpoints/finances/finances";
import { formatCurrencyBR } from "@/features/shared/utils/formatters";
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
import { Input } from "@/components/ui/input";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ExpenseDetailDialogProps {
  expense: ExpenseOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const statusVariant: Record<string, "default" | "destructive" | "outline"> = {
  PAID: "default",
  SETTLED: "default",
  PARTIALLY_PAID: "outline",
  PENDING: "outline",
  OVERDUE: "destructive",
};

const statusLabel: Record<string, string> = {
  PAID: "Pago",
  SETTLED: "Quitada",
  PARTIALLY_PAID: "Parcial",
  PENDING: "Pendente",
  OVERDUE: "Atrasado",
};

const installmentStatusBadge: Record<
  string,
  {
    variant: "default" | "destructive" | "outline";
    label: string;
    icon: React.ReactNode;
  }
> = {
  PAID: {
    variant: "default",
    label: "Pago",
    icon: <Check className="size-3 mr-0.5" />,
  },
  PENDING: {
    variant: "outline",
    label: "Pendente",
    icon: <Clock className="size-3 mr-0.5" />,
  },
  OVERDUE: {
    variant: "destructive",
    label: "Atrasado",
    icon: <AlertTriangle className="size-3 mr-0.5" />,
  },
};

export function ExpenseDetailDialog({
  expense,
  open,
  onOpenChange,
}: ExpenseDetailDialogProps) {
  const queryClient = useQueryClient();
  const [payingUuid, setPayingUuid] = useState<string | null>(null);
  const [showRedistribute, setShowRedistribute] = useState(false);
  const [newNumInstallments, setNewNumInstallments] = useState<number>(
    expense.installments_count ?? 1,
  );
  const [newFirstDueDate, setNewFirstDueDate] = useState<string>(() =>
    new Date().toISOString().slice(0, 10),
  );

  const { data: liveExpenseResponse } = useFinancesExpensesRead(
    expense.uuid,
  );
  const liveExpense = liveExpenseResponse?.data ?? expense;

  const { data: installmentsResponse, isLoading: isLoadingInstallments } =
    useFinancesInstallmentsList({
      expense_id: liveExpense.uuid,
    });

  const markAsPaidMutation = useFinancesInstallmentsMarkAsPaid();
  const unmarkAsPaidMutation = useFinancesInstallmentsUnmarkAsPaid();
  const updateMutation = useFinancesExpensesUpdate();

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
      queryClient.invalidateQueries();
    } catch (error) {
      const action = isPaid ? "desmarcar" : "marcar";
      const { message } = getApiErrorInfo(
        error,
        `Erro ao ${action} parcela.`,
      );
      toast.error(message);
    } finally {
      setPayingUuid(null);
    }
  };

  const handleRedistribute = async () => {
    try {
      await updateMutation.mutateAsync({
        uuid: liveExpense.uuid,
        data: {
          num_installments: newNumInstallments,
          first_due_date: newFirstDueDate || null,
        },
      });
      toast.success("Parcelas remanejadas com sucesso!");
      setShowRedistribute(false);
      queryClient.invalidateQueries();
    } catch (error) {
      const { message } = getApiErrorInfo(
        error,
        "Erro ao remanejar parcelas.",
      );
      toast.error(message);
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
              {statusLabel[liveExpense.status ?? "PENDING"] ??
                liveExpense.status}
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
                  {/* TODO: link para detalhes do contrato */}
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
                {formatCurrencyBR(totalPaid)} de{" "}
                {formatCurrencyBR(actualAmount)}
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          <div>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold">Parcelas</h4>
              {!hasAnyPaid ? (
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-7 text-xs gap-1"
                  onClick={() => {
                    setNewNumInstallments(totalCount);
                    const first = installments[0];
                    setNewFirstDueDate(
                      first
                        ? first.due_date.slice(0, 10)
                        : new Date().toISOString().slice(0, 10),
                    );
                    setShowRedistribute(!showRedistribute);
                  }}
                >
                  <RefreshCw className="size-3" />
                  Remanejar
                </Button>
              ) : null}
            </div>

            {showRedistribute ? (
              <div className="rounded-md border bg-muted/30 p-3 mb-3 space-y-2">
                <div className="flex items-end gap-2">
                  <div className="flex-1">
                    <label className="text-xs font-medium">
                      Nº de Parcelas
                    </label>
                    <Input
                      type="number"
                      min={1}
                      value={newNumInstallments}
                      onChange={(e) =>
                        setNewNumInstallments(
                          Math.max(1, Number(e.target.value) || 1),
                        )
                      }
                      className="h-8 text-sm"
                    />
                  </div>
                  <div className="flex-1">
                    <label className="text-xs font-medium">
                      Venc. 1ª Parcela
                    </label>
                    <Input
                      type="date"
                      value={newFirstDueDate}
                      onChange={(e) => setNewFirstDueDate(e.target.value)}
                      className="h-8 text-sm"
                    />
                  </div>
                  <Button
                    size="sm"
                    className="h-8 text-xs"
                    onClick={handleRedistribute}
                    disabled={updateMutation.isPending}
                  >
                    Aplicar
                  </Button>
                </div>
                {hasAnyPaid ? (
                  <p className="text-xs text-destructive">
                    Não é possível remanejar — há parcelas marcadas como pagas.
                  </p>
                ) : null}
              </div>
            ) : null}

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
                    {installments.map((inst) => {
                      const st = installmentStatusBadge[inst.status] ?? {
                        variant: "outline" as const,
                        label: inst.status,
                        icon: null,
                      };
                      const isPaid = inst.status === "PAID";

                      return (
                        <TableRow key={inst.uuid}>
                          <TableCell className="font-medium text-xs">
                            {inst.installment_number}
                          </TableCell>
                          <TableCell className="text-sm">
                            R$ {formatCurrencyBR(Number(inst.amount))}
                          </TableCell>
                          <TableCell className="text-xs text-muted-foreground">
                            {format(
                              new Date(inst.due_date),
                              "dd/MM/yyyy",
                              { locale: ptBR },
                            )}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={st.variant}
                              className="text-[10px] h-5"
                            >
                              {st.icon}
                              {st.label}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button
                              size="sm"
                              variant={isPaid ? "destructive" : "outline"}
                              className="h-7 text-xs"
                              onClick={() =>
                                togglePayment(inst.uuid, isPaid)
                              }
                              disabled={payingUuid === inst.uuid}
                            >
                              {isPaid ? (
                                <>
                                  <X className="size-3 mr-0.5" />
                                  Desmarcar
                                </>
                              ) : (
                                "Marcar como Pago"
                              )}
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })}
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
