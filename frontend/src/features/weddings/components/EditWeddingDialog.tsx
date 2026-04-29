import { useForm } from "react-hook-form";
import { toast } from "sonner";
import { useEventsUpdateWedding } from "@/api/generated/v1/endpoints/events/events";
import { EventsUpdateWeddingBody } from "@/api/generated/v1/zod/events/events";
import { getApiErrorInfo } from "@/api/error-utils";
import type { WeddingOut } from "@/api/generated/v1/models";
import type { z } from "zod";

type UpdateWeddingFormData = {
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
  const { mutate, isPending } = useEventsUpdateWedding();

  const form = useForm<UpdateWeddingFormData>({
    defaultValues: {
      groom_name: wedding.wedding_detail?.groom_name || "",
      bride_name: wedding.wedding_detail?.bride_name || "",
      date: wedding.date || "",
      location: wedding.location || "",
      expected_guests: wedding.expected_guests ?? undefined,
    },
  });

  const onSubmit = (data: UpdateWeddingFormData) => {
    const payload: z.infer<typeof EventsUpdateWeddingBody> = {
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
      { eventUuid: wedding.uuid, data: payload },
      {
        onSuccess: () => {
          toast.success("Casamento atualizado com sucesso!");
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao atualizar casamento.",
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
          <DialogTitle>Editar Casamento</DialogTitle>
          <DialogDescription>
            Atualize os dados do casamento. As alterações serão salvas
            imediatamente.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form
            onSubmit={form.handleSubmit(onSubmit)}
            className="flex flex-col gap-4"
          >
            <WeddingFormFields form={form} />
            <WeddingDialogActions
              isPending={isPending}
              onCancel={() => onOpenChange(false)}
              submitLabel="Salvar Alterações"
            />
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
