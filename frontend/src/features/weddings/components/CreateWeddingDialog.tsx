import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { useWeddingsCreate } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingsCreateBody } from "@/api/generated/v1/zod/weddings/weddings";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

import { FormDialog } from "@/components/form-dialog";
import { WeddingFormFields } from "./WeddingFormFields";

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

  const form = useForm<CreateWeddingFormData>({
    resolver: zodResolver(WeddingsCreateBody),
    defaultValues: {
      groom_name: "",
      bride_name: "",
      date: "",
      location: "",
      expected_guests: undefined,
    },
  });

  const onSubmit = (data: CreateWeddingFormData) => {
    mutate(
      { data },
      createMutationCallbacks({
        successMsg: "Casamento criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar casamento.",
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
      title="Novo Casamento"
      description="Preencha os dados do novo casamento. Clique em salvar quando terminar."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Criar Casamento"
      maxWidth="600px"
    >
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
