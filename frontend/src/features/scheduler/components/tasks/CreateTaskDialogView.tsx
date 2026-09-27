import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormTextarea } from "@/components/form-fields";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { TASK_PRIORITY_OPTIONS } from "../../constants";
import {
  createTaskSchema,
  type CreateTaskFormData,
} from "../../utils/validation";

export interface CreateTaskDialogViewProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateTaskFormData, onDone: () => void) => void;
  isPending: boolean;
}

export const CreateTaskDialogView = memo(function CreateTaskDialogView({
  open,
  onOpenChange,
  onSubmit,
  isPending,
}: CreateTaskDialogViewProps) {
  const form = useForm<CreateTaskFormData>({
    resolver: zodResolver(createTaskSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "MEDIUM",
      due_date: "",
    },
  });

  const handleOpenChange = (nextOpen: boolean) => {
    if (!nextOpen) {
      form.reset();
    }
    onOpenChange(nextOpen);
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={handleOpenChange}
      title="Novo Item de Checklist"
      description="Cadastre uma tarefa no cronograma operacional do casamento."
      form={form}
      onSubmit={form.handleSubmit((data) => onSubmit(data, () => form.reset()))}
      isPending={isPending}
      submitLabel="Criar Tarefa"
      maxWidth="480px"
    >
      <FormInput
        control={form.control}
        name="title"
        label="Título"
        placeholder="Ex: Degustação do bolo e doces"
      />

      <div className="grid grid-cols-2 gap-4">
        <FormSelect
          control={form.control}
          name="priority"
          label="Prioridade"
          items={TASK_PRIORITY_OPTIONS}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
          placeholder="Selecione"
        />

        <FormField
          control={form.control}
          name="due_date"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Prazo (Opcional)</FormLabel>
              <FormControl>
                <Input
                  type="date"
                  {...field}
                  value={field.value ?? ""}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (Opcional)"
        placeholder="Detalhes ou orientações sobre este item..."
      />
    </FormDialog>
  );
});
