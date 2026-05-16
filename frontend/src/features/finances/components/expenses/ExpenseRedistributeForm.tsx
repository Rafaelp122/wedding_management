import { useState } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import {
  useFinancesExpensesUpdate,
  getFinancesInstallmentsListQueryKey,
  getFinancesExpensesReadQueryKey,
} from "@/api/generated/v1/endpoints/finances/finances";
import { getApiErrorInfo } from "@/api/error-utils";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface ExpenseRedistributeFormProps {
  expenseUuid: string;
  currentCount: number;
  firstExistingDate: string | null;
}

export function ExpenseRedistributeForm({
  expenseUuid,
  currentCount,
  firstExistingDate,
}: ExpenseRedistributeFormProps) {
  const queryClient = useQueryClient();
  const updateMutation = useFinancesExpensesUpdate();

  const [numInstallments, setNumInstallments] = useState(currentCount);
  const [firstDueDate, setFirstDueDate] = useState(
    () => firstExistingDate ?? new Date().toISOString().slice(0, 10),
  );

  const handleApply = async () => {
    try {
      await updateMutation.mutateAsync({
        uuid: expenseUuid,
        data: {
          num_installments: numInstallments,
          first_due_date: firstDueDate || null,
        },
      });
      toast.success("Parcelas remanejadas com sucesso!");
      queryClient.invalidateQueries({
        queryKey: getFinancesInstallmentsListQueryKey({ expense_id: expenseUuid }),
      });
      queryClient.invalidateQueries({
        queryKey: getFinancesExpensesReadQueryKey(expenseUuid),
      });
    } catch (error) {
      const { message } = getApiErrorInfo(error, "Erro ao remanejar parcelas.");
      toast.error(message);
    }
  };

  return (
    <div className="rounded-md border bg-muted/30 p-3 mb-3 space-y-2">
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <label className="text-xs font-medium">Nº de Parcelas</label>
          <Input
            type="number"
            min={1}
            value={numInstallments}
            onChange={(e) =>
              setNumInstallments(Math.max(1, Number(e.target.value) || 1))
            }
            className="h-8 text-sm"
          />
        </div>
        <div className="flex-1">
          <label className="text-xs font-medium">Venc. 1ª Parcela</label>
          <Input
            type="date"
            value={firstDueDate}
            onChange={(e) => setFirstDueDate(e.target.value)}
            className="h-8 text-sm"
          />
        </div>
        <Button
          size="sm"
          className="h-8 text-xs"
          onClick={handleApply}
          disabled={updateMutation.isPending}
        >
          Aplicar
        </Button>
      </div>
    </div>
  );
}
