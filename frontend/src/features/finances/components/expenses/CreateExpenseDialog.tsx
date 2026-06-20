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

import { FormDialog } from "@/components/form-dialog";
import {
  FormInput,
  FormNumber,
  FormSelect,
  FormSelectNullable,
  FormTextarea,
} from "@/components/form-fields";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";

type CreateExpenseFormData = z.infer<typeof FinancesExpensesCreateBody>;

interface CreateExpenseDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateExpenseDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateExpenseDialogProps) {
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

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Nova Despesa"
      description="Registre uma despesa vinculada a uma categoria do orçamento."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Despesa"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome da Despesa"
        placeholder="Ex: Buffet"
      />

      <FormSelect
        control={form.control}
        name="category"
        label="Categoria"
        items={categories}
        getItemKey={(c) => c.uuid}
        getItemLabel={(c) => c.name}
        placeholder="Selecione uma categoria"
      />

      <FormSelectNullable
        control={form.control}
        name="contract"
        label="Contrato (Opcional)"
        items={contracts}
        getItemKey={(c) => c.uuid}
        getItemLabel={(c) => c.description || c.uuid.substring(0, 8)}
        placeholder="Nenhum contrato"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (Opcional)"
        placeholder="Detalhes adicionais da despesa..."
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="estimated_amount"
          label="Valor Estimado"
        />

        <FormNumber
          control={form.control}
          name="actual_amount"
          label="Valor Realizado"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="num_installments"
          label="Nº de Parcelas"
          step="1"
          min={1}
          transformEmptyTo={1}
        />

        <FormField
          control={form.control}
          name="first_due_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Venc. 1ª Parcela</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  {...field}
                  value={field.value ?? ""}
                  onChange={(e) =>
                    field.onChange(
                      e.target.value,
                    )
                  }
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </FormDialog>
  );
}
