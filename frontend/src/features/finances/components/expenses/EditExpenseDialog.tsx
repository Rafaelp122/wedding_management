import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { useFinancesExpensesUpdate } from "@/api/generated/v1/endpoints/finances/finances";
import { useLogisticsContractsList } from "@/api/generated/v1/endpoints/logistics/logistics";
import { FinancesExpensesUpdateBody } from "@/api/generated/v1/zod/finances/finances";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import { selectOnFocus } from "@/lib/select-on-focus";
import { buildPatchPayload } from "@/lib/patch-payload";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";

import { FormDialog } from "@/components/form-dialog";
import {
  FormInput,
  FormNumber,
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

type EditExpenseFormData = z.infer<typeof FinancesExpensesUpdateBody>;

interface EditExpenseDialogProps {
  expense: ExpenseOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditExpenseDialog({
  expense,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditExpenseDialogProps) {
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

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Editar Despesa"
      description="Altere os dados da despesa. A categoria não pode ser alterada."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar Alterações"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome da Despesa"
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
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="estimated_amount"
          label="Valor Estimado"
          disabled={hasPaid}
          onFocus={selectOnFocus}
          transformEmptyTo={0}
        />

        <FormNumber
          control={form.control}
          name="actual_amount"
          label="Valor Realizado"
          disabled={hasPaid}
          onFocus={selectOnFocus}
          transformEmptyTo={0}
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="num_installments"
          label="Nº de Parcelas"
          step="1"
          min={1}
          placeholder="Manter atual"
          disabled={hasPaid}
          transformEmptyTo={""}
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
                  disabled={hasPaid}
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

      {hasPaid && (
        <p className="text-xs text-muted-foreground">
          Valores e parcelamento bloqueados — há parcelas marcadas como
          pagas. Crie uma nova despesa se precisar alterar valores.
        </p>
      )}
    </FormDialog>
  );
}
