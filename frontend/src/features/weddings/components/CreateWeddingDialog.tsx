import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { useEventsCreateWedding } from "@/api/generated/v1/endpoints/events/events";
import { EventsCreateWeddingBody } from "@/api/generated/v1/zod/events/events";
import { getApiErrorInfo } from "@/api/error-utils";
import type { z } from "zod";

type CreateWeddingFormData = {
  groom_name: string;
  bride_name: string;
  date: string;
  location: string;
  expected_guests?: number;
};

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Form } from "@/components/ui/form";
import { WeddingDialogActions } from "./WeddingDialogActions";
import { WeddingFormFields } from "./WeddingFormFields";

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
  const { mutate, isPending } = useEventsCreateWedding();

  const form = useForm<CreateWeddingFormData>({
    defaultValues: {
      groom_name: "",
      bride_name: "",
      date: "",
      location: "",
      expected_guests: undefined,
    },
  });

  const onSubmit = (data: CreateWeddingFormData) => {
    const payload: z.infer<typeof EventsCreateWeddingBody> = {
      name: `${data.groom_name} & ${data.bride_name}`,
      event_type: "WEDDING",
      date: data.date,
      location: data.location,
      expected_guests: data.expected_guests,
      wedding_detail: {
        groom_name: data.groom_name,
        bride_name: data.bride_name,
      },
    };

    mutate(
      { data: payload },
      {
        onSuccess: () => {
          toast.success("Casamento criado com sucesso!");
          form.reset();
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao criar casamento.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Novo Casamento</DialogTitle>
          <DialogDescription>
            Preencha os dados do novo casamento. Clique em salvar quando
            terminar.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <WeddingFormFields
              form={form}
              placeholders={{
                groom_name: "João Silva",
                bride_name: "Maria Santos",
                location: "Salão de Festas Jardim Encantado",
              }}
              expectedGuestsLabel="Número de Convidados (Opcional)"
            />
            <WeddingDialogActions
              isPending={isPending}
              onCancel={() => onOpenChange(false)}
              submitLabel="Criar Casamento"
            />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
