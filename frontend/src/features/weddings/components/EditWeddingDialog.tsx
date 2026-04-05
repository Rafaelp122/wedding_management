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
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";

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
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="groom_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome do Noivo</FormLabel>
                    <FormControl>
                      <Input {...field} value={field.value || ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="bride_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome da Noiva</FormLabel>
                    <FormControl>
                      <Input {...field} value={field.value || ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="date"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Data do Casamento</FormLabel>
                    <FormControl>
                      <Input type="date" {...field} value={field.value || ""} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="expected_guests"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Número de Convidados</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        {...field}
                        value={field.value ?? ""}
                        onChange={(e) => {
                          const value = e.target.value;
                          field.onChange(
                            value === "" ? undefined : Number(value),
                          );
                        }}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <FormField
              control={form.control}
              name="location"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Local</FormLabel>
                  <FormControl>
                    <Input {...field} value={field.value || ""} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={() => onOpenChange(false)}
                disabled={isPending}
              >
                Cancelar
              </Button>
              <Button type="submit" disabled={isPending}>
                {isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Salvar Alterações
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
