import { useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useFinancesExpensesCreate,
  useFinancesCategoriesList,
} from "@/api/generated/v1/endpoints/finances/finances";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { FinancesExpensesCreateBody } from "@/api/generated/v1/zod/finances/finances";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

export type CreateExpenseFormData = z.input<typeof FinancesExpensesCreateBody>;

export interface UseCreateExpenseFormProps {
  weddingUuid: string;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

/**
 * Hook para gerenciar a lógica do formulário de criação de despesa.
 * Encapsula formulário, busca de categorias e contratos para seleção,
 * mutação de criação e gerenciamento de callbacks de toast e resete de estado.
 *
 * @param props Propriedades de configuração contendo o ID do casamento e callbacks.
 * @returns Instância do formulário, listas de categorias/contratos, estado de pendência e handlers.
 */
export function useCreateExpenseForm({
  weddingUuid,
  onOpenChange,
  onSuccess,
}: UseCreateExpenseFormProps) {
  const { mutate, isPending } = useFinancesExpensesCreate();

  const { data: categoriesResponse } = useFinancesCategoriesList({
    wedding_id: weddingUuid,
  });
  const categories = categoriesResponse?.data?.items || [];

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items || [];

  const form = useForm<CreateExpenseFormData>({
    resolver: zodResolver(FinancesExpensesCreateBody),
    defaultValues: {
      category: "",
      contract: null,
      name: "",
      description: "",
      estimated_amount: undefined,
      actual_amount: undefined,
      num_installments: 1,
      first_due_date: new Date().toISOString().slice(0, 10),
    },
  });

  const handleOpenChange = useCallback(
    (newOpen: boolean) => {
      if (!newOpen) {
        form.reset();
      }
      onOpenChange(newOpen);
    },
    [form, onOpenChange],
  );

  const onSubmit = (data: CreateExpenseFormData) => {
    mutate(
      { data },
      createMutationCallbacks({
        successMsg: "Despesa criada com sucesso!",
        fallbackErrorMsg: "Erro ao criar despesa.",
        onSuccess: () => {
          form.reset();
          onSuccess();
        },
      }),
    );
  };

  return {
    form,
    categories,
    contracts,
    isPending,
    handleOpenChange,
    onSubmit,
  };
}
