import { useState } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import {
  useFinancesInstallmentsList,
  useFinancesInstallmentsMarkAsPaid,
  useFinancesInstallmentsUnmarkAsPaid,
  useFinancesExpensesRead,
  getFinancesInstallmentsListQueryKey,
  getFinancesExpensesReadQueryKey,
} from "@/api/generated/v1/endpoints/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";

import { ExpenseDetailSheetPresenter } from "./ExpenseDetailSheetPresenter";

interface ExpenseDetailSheetProps {
  expense: ExpenseOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ExpenseDetailSheet({
  expense,
  open,
  onOpenChange,
}: ExpenseDetailSheetProps) {
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
    <ExpenseDetailSheetPresenter
      expense={liveExpense}
      installments={installments}
      open={open}
      onOpenChange={onOpenChange}
      isLoadingInstallments={isLoadingInstallments}
      payingUuid={payingUuid}
      onTogglePayment={togglePayment}
      showRedistribute={showRedistribute}
      onToggleRedistribute={() => setShowRedistribute((prev) => !prev)}
    />
  );
}
