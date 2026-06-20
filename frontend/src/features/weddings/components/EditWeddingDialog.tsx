import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { useWeddingsUpdate } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingsUpdateBody } from "@/api/generated/v1/zod/weddings/weddings";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";

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

const WEDDING_STATUS_OPTIONS = [
  { value: "IN_PROGRESS", label: "Em Andamento" },
  { value: "COMPLETED", label: "Concluído" },
  { value: "CANCELED", label: "Cancelado" },
] as const;

type UpdateWeddingFormData = z.input<typeof WeddingsUpdateBody>;

interface EditWeddingDialogProps {
  wedding: WeddingOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export function EditWeddingDialog({
  wedding,
  open,
  onOpenChange,
  onSuccess,
}: EditWeddingDialogProps) {
  const { mutate, isPending } = useWeddingsUpdate();

  const form = useForm<UpdateWeddingFormData>({
    resolver: zodResolver(WeddingsUpdateBody),
    defaultValues: {
      groom_name: wedding.groom_name || "",
      bride_name: wedding.bride_name || "",
      date: wedding.date || "",
      location: wedding.location || "",
      expected_guests: wedding.expected_guests ?? undefined,
      status: wedding.status || "IN_PROGRESS",
    },
  });

  const onSubmit = (data: UpdateWeddingFormData) => {
    mutate(
      { uuid: wedding.uuid, data },
      createMutationCallbacks({
        successMsg: "Casamento atualizado com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar casamento.",
        onSuccess: () => onSuccess(),
      }),
    );
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Editar Casamento"
      description="Atualize os dados do casamento. As alterações serão salvas imediatamente."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar Alterações"
      maxWidth="600px"
    >
      <WeddingFormFields form={form} />

      <FormField
        control={form.control}
        name="status"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Status</FormLabel>
            <Select
              onValueChange={field.onChange}
              value={field.value ?? "IN_PROGRESS"}
            >
              <FormControl>
                <SelectTrigger>
                  <SelectValue placeholder="Selecione o status" />
                </SelectTrigger>
              </FormControl>
              <SelectContent>
                {WEDDING_STATUS_OPTIONS.map((opt) => (
                  <SelectItem key={opt.value} value={opt.value}>
                    {opt.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <FormMessage />
          </FormItem>
        )}
      />
    </FormDialog>
  );
}
