import { useCreateExpenseForm } from "../../hooks/useCreateExpenseForm";
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
  const { form, categories, contracts, isPending, onSubmit, handleOpenChange } =
    useCreateExpenseForm({
      weddingUuid,
      onOpenChange,
      onSuccess,
    });

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
      title="Nova Despesa"
      description="Cadastre uma nova despesa no orçamento."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Despesa"
      maxWidth="560px"
    >
      <FormSelect
        control={form.control}
        name="category"
        label="Categoria"
        items={categories}
        getItemKey={(cat) => cat.uuid}
        getItemLabel={(cat) => cat.name}
        placeholder="Selecione uma categoria"
      />

      <FormInput
        control={form.control}
        name="name"
        label="Nome da Despesa"
        placeholder="Ex: Buffet Completo"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição"
        placeholder="Detalhes adicionais..."
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
          label="Valor Real (Contratado)"
        />
      </div>

      <FormSelectNullable
        control={form.control}
        name="contract"
        label="Contrato Associado (Opcional)"
        items={contracts}
        getItemKey={(c) => c.uuid}
        getItemLabel={(c) => c.name || c.description || c.uuid.substring(0, 8)}
        placeholder="Nenhum (Despesa sem contrato)"
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="num_installments"
          label="Nº de Parcelas"
          min={1}
        />
        <FormField
          control={form.control}
          name="first_due_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>1º Vencimento</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  value={field.value ?? ""}
                  onChange={(e) => field.onChange(e.target.value)}
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
