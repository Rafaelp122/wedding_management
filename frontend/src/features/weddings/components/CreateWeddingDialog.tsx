import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { toast } from "sonner";
import { useWeddingsCreate } from "@/api/generated/v1/endpoints/weddings/weddings";
import { WeddingsCreateBody } from "@/api/generated/v1/zod/weddings/weddings";
import { getApiErrorInfo } from "@/api/error-utils";
import type { z } from "zod";

type CreateWeddingFormData = z.infer<typeof WeddingsCreateBody>;

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
            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="groom_name"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Nome do Noivo</FormLabel>
                    <FormControl>
                      <Input placeholder="João Silva" {...field} />
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
                      <Input placeholder="Maria Santos" {...field} />
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
                      <Input type="date" {...field} />
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
                    <FormLabel>Número de Convidados (Opcional)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        placeholder="150"
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
                    <Input
                      placeholder="Salão de Festas Jardim Encantado"
                      {...field}
                    />
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
                Criar Casamento
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
