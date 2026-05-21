import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";

import { useWeddingsCreate } from "@/api/generated/v1/endpoints/weddings/weddings";
import { getSchedulerEventsListQueryKey } from "@/api/generated/v1/endpoints/scheduler/scheduler";
import { getDashboardSummaryQueryKey } from "@/api/generated/v1/endpoints/dashboard/dashboard";
import { WeddingsCreateBody } from "@/api/generated/v1/zod/weddings/weddings";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { WeddingFormFields } from "./WeddingFormFields";

const TEMPLATE_OPTIONS = [
  { value: "none", label: "Começar do zero" },
  { value: "religious_12m", label: "Religioso (12 meses)" },
  { value: "beach_6m", label: "Praia (6 meses)" },
  { value: "civil_buffet_3m", label: "Civil + Buffet (3 meses)" },
] as const;

type CreateWeddingFormData = z.infer<typeof WeddingsCreateBody>;

interface CreateWeddingDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function CreateWeddingDialog({
  open,
  onOpenChange,
  onSuccess,
}: CreateWeddingDialogProps) {
  const { mutate, isPending } = useWeddingsCreate();
  const queryClient = useQueryClient();

  const form = useForm<CreateWeddingFormData>({
    resolver: zodResolver(WeddingsCreateBody),
    defaultValues: {
      groom_name: "",
      bride_name: "",
      date: "",
      location: "",
      expected_guests: undefined,
      template: null,
    },
  });

  const onSubmit = (data: CreateWeddingFormData) => {
    const payload = {
      ...data,
      // Se o template for "none", não enviar (null)
      template: data.template === "none" ? null : data.template,
    };

    mutate(
      { data: payload },
      createMutationCallbacks({
        successMsg: "Casamento criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar casamento.",
        onSuccess: () => {
          form.reset();
          queryClient.invalidateQueries({ queryKey: getSchedulerEventsListQueryKey() });
          queryClient.invalidateQueries({ queryKey: getDashboardSummaryQueryKey() });
          onSuccess();
        },
      }),
    );
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Novo Casamento"
      description="Preencha os dados do novo casamento. Clique em salvar quando terminar."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Casamento"
      maxWidth="600px"
    >
      {/* Template selector */}
      <FormField
        control={form.control}
        name="template"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Modelo de Cronograma</FormLabel>
            <Select
              onValueChange={(value) =>
                field.onChange(value === "none" ? null : value)
              }
              value={field.value ?? "none"}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione um modelo" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {TEMPLATE_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">
              Modelos de cronograma criam eventos automaticamente com base no
              tipo de cerimônia.
            </p>
            <FormMessage />
          </FormItem>
        )}
      />

      <WeddingFormFields
        form={form}
        placeholders={{
          groom_name: "João Silva",
          bride_name: "Maria Santos",
          location: "Salão de Festas Jardim Encantado",
        }}
        expectedGuestsLabel="Número de Convidados (Opcional)"
      />
    </FormDialog>
  );
}
