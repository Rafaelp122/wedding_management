import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { useWeddingsPartialUpdate } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingsPartialUpdateBody } from "@/api/generated/v1/zod/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { WeddingOut } from "@/api/generated/v1/models";
import type { z } from "zod";

type UpdateWeddingFormData = z.infer<typeof WeddingsPartialUpdateBody>;

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
  const { mutate, isPending } = useWeddingsPartialUpdate();

  const form = useForm<UpdateWeddingFormData>({
    resolver: zodResolver(WeddingsPartialUpdateBody),
    defaultValues: {
      groom_name: wedding.groom_name || "",
      bride_name: wedding.bride_name || "",
      date: wedding.date || "",
      location: wedding.location || "",
      expected_guests: wedding.expected_guests ?? undefined,
    },
  });

  const onSubmit = (data: UpdateWeddingFormData) => {
    mutate(
      { uuid: wedding.uuid, data },
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
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
