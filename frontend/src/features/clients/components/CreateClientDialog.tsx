import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import type { ClientOut } from "@/api/generated/v1/models/clientOut";
import {
  useCreateClient,
  useUpdateClient,
  getListClientsQueryKey,
} from "@/api/generated/v1/endpoints/clients/clients";

import { FormDialog } from "@/components/form-dialog";
import {
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";

const clientFormSchema = z.object({
  name: z.string().min(2, "Nome deve ter ao menos 2 caracteres"),
  cpf: z.string(),
  email: z.string().email("E-mail inválido").or(z.literal("")),
  phone: z.string(),
  notes: z.string(),
});

type ClientFormData = z.infer<typeof clientFormSchema>;

interface CreateClientDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  client?: ClientOut | null;
}

/**
 * Smart Component modal para criação ou edição de cliente (ADR-024).
 */
export function CreateClientDialog({
  open,
  onOpenChange,
  client,
}: CreateClientDialogProps) {
  const isEditing = Boolean(client);
  const queryClient = useQueryClient();

  const createMutation = useCreateClient({
    mutation: {
      onSuccess: () => {
        toast.success("Cliente cadastrado com sucesso!");
        queryClient.invalidateQueries({ queryKey: getListClientsQueryKey() });
        onOpenChange(false);
      },
      onError: (err: unknown) => {
        const errorMsg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Erro ao cadastrar cliente.";
        toast.error(errorMsg);
      },
    },
  });

  const updateMutation = useUpdateClient({
    mutation: {
      onSuccess: () => {
        toast.success("Dados do cliente atualizados!");
        queryClient.invalidateQueries({ queryKey: getListClientsQueryKey() });
        onOpenChange(false);
      },
      onError: (err: unknown) => {
        const errorMsg =
          (err as { response?: { data?: { detail?: string } } })?.response?.data
            ?.detail || "Erro ao atualizar cliente.";
        toast.error(errorMsg);
      },
    },
  });

  const form = useForm<ClientFormData>({
    resolver: zodResolver(clientFormSchema),
    defaultValues: {
      name: "",
      cpf: "",
      email: "",
      phone: "",
      notes: "",
    },
  });

  useEffect(() => {
    if (open) {
      if (client) {
        form.reset({
          name: client.name || "",
          cpf: client.cpf || "",
          email: client.email || "",
          phone: client.phone || "",
          notes: client.notes || "",
        });
      } else {
        form.reset({
          name: "",
          cpf: "",
          email: "",
          phone: "",
          notes: "",
        });
      }
    }
  }, [open, client, form]);

  const onSubmit = (data: ClientFormData) => {
    if (isEditing && client) {
      updateMutation.mutate({
        uuid: client.uuid,
        data: {
          name: data.name,
          cpf: data.cpf || undefined,
          email: data.email || undefined,
          phone: data.phone || undefined,
          notes: data.notes || undefined,
        },
      });
    } else {
      createMutation.mutate({
        data: {
          name: data.name,
          cpf: data.cpf || undefined,
          email: data.email || undefined,
          phone: data.phone || undefined,
          notes: data.notes || undefined,
        },
      });
    }
  };

  const isPending = createMutation.isPending || updateMutation.isPending;

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={isEditing ? "Editar Cliente" : "Novo Cliente"}
      description={
        isEditing
          ? "Atualize as informações cadastrais do cliente."
          : "Cadastre uma nova pessoa física no catálogo de contatos e clientes."
      }
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel={isEditing ? "Salvar Alterações" : "Cadastrar Cliente"}
    >
      <div className="space-y-4">
          <FormField
            control={form.control}
            name="name"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Nome Completo *</FormLabel>
                <FormControl>
                  <Input
                    placeholder="Ex: Juliana Vasconcelos"
                    disabled={isPending}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <FormField
              control={form.control}
              name="cpf"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>CPF</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="000.000.000-00"
                      disabled={isPending}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="phone"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Telefone / WhatsApp</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="(11) 98765-4321"
                      disabled={isPending}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
          </div>

          <FormField
            control={form.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>E-mail</FormLabel>
                <FormControl>
                  <Input
                    type="email"
                    placeholder="juliana@exemplo.com"
                    disabled={isPending}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="notes"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Observações</FormLabel>
                <FormControl>
                  <Textarea
                    placeholder="Observações internas sobre o cliente, preferências ou parentescos."
                    className="resize-none h-20"
                    disabled={isPending}
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

      </div>
    </FormDialog>
  );
}
