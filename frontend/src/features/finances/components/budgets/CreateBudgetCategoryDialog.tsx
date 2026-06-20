import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useFinancesCategoriesCreate,
  useFinancesBudgetsForWedding,
} from "@/api/generated/v1/endpoints/finances/finances";
import { FinancesCategoriesCreateBody } from "@/api/generated/v1/zod/finances/finances";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormNumber, FormTextarea } from "@/components/form-fields";

type CreateCategoryFormData = z.input<typeof FinancesCategoriesCreateBody>;

interface CreateBudgetCategoryDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateBudgetCategoryDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateBudgetCategoryDialogProps) {
  const { mutate, isPending } = useFinancesCategoriesCreate();
  const { data: budgetResponse } = useFinancesBudgetsForWedding(weddingUuid, {
    query: { enabled: open },
  });
  const budget = budgetResponse?.data;

  const form = useForm<CreateCategoryFormData>({
    resolver: zodResolver(FinancesCategoriesCreateBody),
    defaultValues: {
      budget: "",
      name: "",
      description: "",
      allocated_budget: undefined,
    },
  });

  useEffect(() => {
    if (budget?.uuid) {
      form.setValue("budget", budget.uuid);
    }
  }, [budget?.uuid, form]);

  const handleSubmit = form.handleSubmit((data) => {
    mutate(
      { data },
      createMutationCallbacks({
        successMsg: "Categoria criada com sucesso!",
        fallbackErrorMsg: "Falha ao criar categoria.",
        onSuccess: () => {
          form.reset();
          onOpenChange(false);
          onSuccess();
        },
      }),
    );
  });

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Nova Categoria"
      description="Adicione um novo grupo de custos ao orçamento."
      form={form}
      onSubmit={handleSubmit}
      isPending={isPending}
      submitDisabled={isPending || !budget}
      submitLabel="Criar Categoria"
      maxWidth="425px"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
        placeholder="Ex: Buffet, Decoração..."
      />

      <FormNumber
        control={form.control}
        name="allocated_budget"
        label="Valor Orçado (R$)"
        placeholder="0,00"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (opcional)"
        placeholder="Detalhes sobre esta categoria..."
      />
    </FormDialog>
  );
}
