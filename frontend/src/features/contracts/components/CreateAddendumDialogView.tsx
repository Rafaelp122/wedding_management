import { memo, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

import { FormDialog } from "@/components/form-dialog";
import { FormCurrency, FormTextarea } from "@/components/form-fields";

const createAddendumSchema = z.object({
  amount: z
    .number({ message: "Informe um valor válido" })
    .positive("O valor do aditivo deve ser positivo"),
  justification: z
    .string()
    .trim()
    .min(1, "A justificativa é obrigatória"),
});

export type CreateAddendumFormData = z.infer<typeof createAddendumSchema>;

export interface CreateAddendumDialogViewProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateAddendumFormData) => void;
  isPending: boolean;
}

export const CreateAddendumDialogView = memo(function CreateAddendumDialogView({
  open,
  onOpenChange,
  onSubmit,
  isPending,
}: CreateAddendumDialogViewProps) {
  const form = useForm<CreateAddendumFormData>({
    resolver: zodResolver(createAddendumSchema),
    defaultValues: {
      amount: 0,
      justification: "",
    },
  });

  useEffect(() => {
    if (open) {
      form.reset({
        amount: 0,
        justification: "",
      });
    }
  }, [open, form]);

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Novo Termo Aditivo"
      description="Informe o valor e a justificativa para adicionar um termo aditivo ao contrato."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Aditivo"
      maxWidth="480px"
    >
      <div className="space-y-4">
        <FormCurrency
          control={form.control}
          name="amount"
          label="Valor do Aditivo (R$)"
          placeholder="0,00"
        />
        <FormTextarea
          control={form.control}
          name="justification"
          label="Justificativa do Aditivo"
          placeholder="Ex: Acréscimo de 20 convidados e extensão de 1 hora de serviço..."
        />
      </div>
    </FormDialog>
  );
});
