import { selectOnFocus } from "@/lib/select-on-focus";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";
import { useEditExpenseForm } from "../../hooks/useEditExpenseForm";

import { FormDialog } from "@/components/form-dialog";
import {
  FormInput,
  FormNumber,
  FormSelectNullable,
  FormTextarea,
} from "@/components/form-fields";

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
  const { form, contracts, hasPaid, isPending, onSubmit, handleOpenChange } =
    useEditExpenseForm({
      expense,
      weddingUuid,
      open,
      onOpenChange,
      onSuccess,
    });

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
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
        getItemLabel={(c) => c.name || c.uuid.substring(0, 8)}
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

      {hasPaid && (
        <p className="text-xs text-muted-foreground">
          Valor realizado bloqueado — há parcelas marcadas como pagas. Crie uma nova despesa se precisar alterar o valor realizado.
        </p>
      )}
    </FormDialog>
  );
}
