import { useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { useFinancesExpensesUpdate } from "@/api/generated/v1/endpoints/finances/finances";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { FinancesExpensesUpdateBody } from "@/api/generated/v1/zod/finances/finances";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import { buildPatchPayload } from "@/lib/patch-payload";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";

export type EditExpenseFormData = z.input<typeof FinancesExpensesUpdateBody>;

export interface UseEditExpenseFormProps {
  expense: ExpenseOut;
  weddingUuid: string;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

/**
 * Hook para gerenciar o formulário de edição de despesa.
 * Encapsula formulário, busca de contratos disponíveis, cálculo de campos alterados (PATCH payload)
 * via `buildPatchPayload` e controle de bloqueio de edição quando há parcelas pagas.
 *
 * @param props Propriedades de configuração incluindo despesa a editar e callbacks.
 * @returns Instância do formulário, lista de contratos, flag de bloqueio `hasPaid` e handlers.
 */
export function useEditExpenseForm({
  expense,
  weddingUuid,
  onOpenChange,
  onSuccess,
}: UseEditExpenseFormProps) {
  const { mutate, isPending } = useFinancesExpensesUpdate();

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items || [];

  const hasPaid = (expense.paid_installments_count ?? 0) > 0;

  const form = useForm<EditExpenseFormData>({
    resolver: zodResolver(FinancesExpensesUpdateBody),
    defaultValues: {
      name: expense.name || "",
      description: expense.description || "",
      estimated_amount: Number(expense.estimated_amount) || 0,
      actual_amount: Number(expense.actual_amount) || 0,
      contract: expense.contract || null,
      num_installments: null,
      first_due_date: null,
    },
  });

  const handleOpenChange = useCallback(
    (newOpen: boolean) => {
      onOpenChange(newOpen);
    },
    [onOpenChange],
  );

  const onSubmit = (data: EditExpenseFormData) => {
    const original: Record<string, unknown> = {
      name: expense.name || "",
      description: expense.description || "",
      estimated_amount: Number(expense.estimated_amount) || 0,
      actual_amount: Number(expense.actual_amount) || 0,
      contract: expense.contract || null,
      num_installments: null,
      first_due_date: null,
    };
    const modified: Record<string, unknown> = {
      name: data.name,
      description: data.description,
      estimated_amount: Number(data.estimated_amount) || 0,
      actual_amount: Number(data.actual_amount) || 0,
      contract: data.contract,
      num_installments: data.num_installments ?? null,
      first_due_date: data.first_due_date ?? null,
    };
    const payload = buildPatchPayload(original, modified, [
      "name",
      "description",
      "estimated_amount",
      "actual_amount",
      "contract",
      "num_installments",
      "first_due_date",
    ]);

    mutate(
      { uuid: expense.uuid, data: payload },
      createMutationCallbacks({
        successMsg: "Despesa atualizada com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar despesa.",
        onSuccess: () => onSuccess(),
      }),
    );
  };

  return {
    form,
    contracts,
    hasPaid,
    isPending,
    handleOpenChange,
    onSubmit,
  };
}
