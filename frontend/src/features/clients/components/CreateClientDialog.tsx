import { memo, useEffect } from "react";
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

import { CreateClientDialogView } from "./CreateClientDialogView";

export const clientFormSchema = z.object({
  name: z.string().min(2, "Nome deve ter ao menos 2 caracteres"),
  cpf: z.string(),
  email: z.string().email("E-mail inválido").or(z.literal("")),
  phone: z.string(),
  notes: z.string(),
});

export type ClientFormData = z.infer<typeof clientFormSchema>;

export interface CreateClientDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  client?: ClientOut | null;
}

/**
 * Smart Component modal para criação ou edição de cliente (ADR-012, ADR-024).
 */
export const CreateClientDialog = memo(function CreateClientDialog({
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
    <CreateClientDialogView
      open={open}
      onOpenChange={onOpenChange}
      isEditing={isEditing}
      form={form}
      onSubmit={onSubmit}
      isPending={isPending}
    />
  );
});
