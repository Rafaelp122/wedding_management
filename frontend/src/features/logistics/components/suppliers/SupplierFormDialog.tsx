import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useLogisticsSuppliersCreate,
  useLogisticsSuppliersUpdate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsSuppliersCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";

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
import { FormInput } from "@/components/form-fields";

type SupplierFormData = z.infer<typeof LogisticsSuppliersCreateBody>;

interface SupplierFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  supplier: SupplierOut | null;
  onSuccess: () => void;
}

export function SupplierFormDialog({
  open,
  onOpenChange,
  mode,
  supplier,
  onSuccess,
}: SupplierFormDialogProps) {
  const createMutation = useLogisticsSuppliersCreate();
  const updateMutation = useLogisticsSuppliersUpdate();
  const isPending = mode === "create" ? createMutation.isPending : updateMutation.isPending;

  const form = useForm({
    resolver: zodResolver(LogisticsSuppliersCreateBody),
    defaultValues: {
      name: "",
      cnpj: "",
      phone: "",
      email: "",
      is_active: true,
    } as SupplierFormData,
  });

  useEffect(() => {
    if (open) {
      if (mode === "edit" && supplier) {
        form.reset({
          name: supplier.name,
          cnpj: supplier.cnpj,
          phone: supplier.phone,
          email: supplier.email,
          is_active: supplier.is_active,
        });
      } else {
        form.reset({
          name: "",
          cnpj: "",
          phone: "",
          email: "",
          is_active: true,
        });
      }
    }
  }, [open, mode, supplier, form]);

  const onSubmit = (data: SupplierFormData) => {
    if (mode === "create") {
      createMutation.mutate(
        { data },
        createMutationCallbacks({
          successMsg: "Fornecedor criado com sucesso!",
          fallbackErrorMsg: "Não foi possível salvar o fornecedor.",
          onSuccess: () => {
            form.reset();
            onSuccess();
          },
        }),
      );
    } else if (supplier) {
      updateMutation.mutate(
        { uuid: supplier.uuid, data },
        createMutationCallbacks({
          successMsg: "Fornecedor atualizado com sucesso!",
          fallbackErrorMsg: "Não foi possível salvar o fornecedor.",
          onSuccess: () => onSuccess(),
        }),
      );
    }
  };

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title={mode === "create" ? "Novo fornecedor" : "Editar fornecedor"}
      description="Preencha os dados principais para manter o cadastro de fornecedores."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
        placeholder="Nome do fornecedor"
      />

      <div className="grid grid-cols-2 gap-4">
        <FormInput
          control={form.control}
          name="email"
          label="E-mail"
          type="email"
          placeholder="contato@fornecedor.com"
        />

        <FormInput
          control={form.control}
          name="phone"
          label="Telefone"
          type="tel"
          placeholder="(21) 99999-9999"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormInput
          control={form.control}
          name="cnpj"
          label="CNPJ"
          placeholder="00.000.000/0000-00"
        />

        <FormField
          control={form.control}
          name="is_active"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Status</FormLabel>
              <Select
                onValueChange={(v) => field.onChange(v === "true")}
                value={field.value ? "true" : "false"}
              >
                <FormControl>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                </FormControl>
                <SelectContent>
                  <SelectItem value="true">Ativo</SelectItem>
                  <SelectItem value="false">Inativo</SelectItem>
                </SelectContent>
              </Select>
              <FormMessage />
            </FormItem>
          )}
        />
      </div>
    </FormDialog>
  );
}
