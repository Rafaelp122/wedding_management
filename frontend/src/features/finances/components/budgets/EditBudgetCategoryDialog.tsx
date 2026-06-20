import { useForm, useWatch } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { AlertCircle } from "lucide-react";

import { useFinancesCategoriesUpdate } from "@/api/generated/v1/endpoints/finances/finances";
import { FinancesCategoriesUpdateBody } from "@/api/generated/v1/zod/finances/finances";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { BudgetCategoryOut } from "@/api/generated/v1/models/budgetCategoryOut";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormNumber, FormTextarea } from "@/components/form-fields";

type EditCategoryFormData = z.infer<typeof FinancesCategoriesUpdateBody>;

interface EditBudgetCategoryDialogProps {
  category: BudgetCategoryOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditBudgetCategoryDialog({
  category,
  open,
  onOpenChange,
  onSuccess,
}: EditBudgetCategoryDialogProps) {
  const { mutate, isPending } = useFinancesCategoriesUpdate();

  const form = useForm<EditCategoryFormData>({
    resolver: zodResolver(FinancesCategoriesUpdateBody),
    defaultValues: {
      name: category.name,
      description: category.description ?? "",
      allocated_budget: parseFloat(category.allocated_budget),
    },
  });

  const handleSubmit = form.handleSubmit((data) => {
    mutate(
      { uuid: category.uuid, data },
      createMutationCallbacks({
        successMsg: "Categoria atualizada com sucesso!",
        fallbackErrorMsg: "Falha ao atualizar categoria.",
        onSuccess: () => {
          onOpenChange(false);
          onSuccess();
        },
      }),
    );
  });

  const currentSpent = parseFloat(category.total_spent ?? "0");
  const watchAllocated = useWatch({ control: form.control, name: "allocated_budget" });
  const numericValue =
    watchAllocated !== null && watchAllocated !== undefined
      ? Number(watchAllocated)
      : null;
  const valueBelowSpent = numericValue !== null && numericValue < currentSpent;

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Editar Categoria"
      description={`Altere o nome ou valor orçado da categoria ${category.name}.`}
      form={form}
      onSubmit={handleSubmit}
      isPending={isPending}
      submitLabel="Salvar"
      maxWidth="425px"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
        placeholder="Nome da categoria"
      />

      <FormNumber
        control={form.control}
        name="allocated_budget"
        label="Valor Orçado (R$)"
        placeholder="0,00"
        transformEmptyTo={""}
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (opcional)"
        placeholder="Detalhes sobre esta categoria..."
      />

      {valueBelowSpent && (
        <div className="flex items-start gap-2 p-3 rounded-md bg-amber-50 dark:bg-amber-950/30 text-amber-800 dark:text-amber-200 text-sm">
          <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
          <span>
            O novo valor é menor que o total já gasto (R${" "}
            {currentSpent.toLocaleString("pt-BR", {
              minimumFractionDigits: 2,
            })}
            ).
          </span>
        </div>
      )}
    </FormDialog>
  );
}
