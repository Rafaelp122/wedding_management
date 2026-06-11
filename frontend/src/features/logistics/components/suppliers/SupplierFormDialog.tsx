import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";

import {
  useLogisticsSuppliersCreate,
  useLogisticsSuppliersUpdate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";

import {
  SupplierFormSchema,
  type SupplierFormData,
} from "@/features/logistics/hooks/supplierFormSchema";

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
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { FormInput } from "@/components/form-fields";

function applyCnpjMask(value: string): string {
  const digits = value.replace(/\D/g, "").slice(0, 14);

  let masked = digits;
  if (digits.length > 2) masked = `${digits.slice(0, 2)}.${digits.slice(2)}`;
  if (digits.length > 5) masked = `${masked.slice(0, 6)}.${masked.slice(6)}`;
  if (digits.length > 8) masked = `${masked.slice(0, 10)}/${masked.slice(10)}`;
  if (digits.length > 12) masked = `${masked.slice(0, 15)}-${masked.slice(15)}`;

  return masked;
}

const EMPTY_VALUES: SupplierFormData = {
  name: "",
  cnpj: "",
  phone: "",
  email: "",
  is_active: true,
  address: "",
  city: "",
  state: "",
  website: "",
  notes: "",
};

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
    resolver: zodResolver(SupplierFormSchema),
    defaultValues: EMPTY_VALUES,
  });

  useEffect(() => {
    if (open) {
      if (mode === "edit" && supplier) {
        form.reset({
          name: supplier.name,
          cnpj: supplier.cnpj ?? "",
          phone: supplier.phone,
          email: supplier.email,
          is_active: supplier.is_active,
          address: supplier.address ?? "",
          city: supplier.city ?? "",
          state: supplier.state ?? "",
          website: supplier.website ?? "",
          notes: supplier.notes ?? "",
        });
      } else {
        form.reset(EMPTY_VALUES);
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
        <FormField
          control={form.control}
          name="cnpj"
          render={({ field }) => (
            <FormItem>
              <FormLabel>CNPJ</FormLabel>
              <FormControl>
                <Input
                  placeholder="00.000.000/0000-00"
                  value={field.value ?? ""}
                  onChange={(e) => field.onChange(applyCnpjMask(e.target.value))}
                  onBlur={field.onBlur}
                  name={field.name}
                  ref={field.ref}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
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

      <FormField
        control={form.control}
        name="address"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Endereço</FormLabel>
            <FormControl>
              <Input
                placeholder="Rua, número, bairro"
                value={field.value ?? ""}
                onChange={field.onChange}
                onBlur={field.onBlur}
                name={field.name}
                ref={field.ref}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />

      <div className="grid grid-cols-2 gap-4">
        <FormInput
          control={form.control}
          name="city"
          label="Cidade"
          placeholder="São Paulo"
        />

        <FormInput
          control={form.control}
          name="state"
          label="Estado (UF)"
          placeholder="SP"
        />
      </div>

      <FormInput
        control={form.control}
        name="website"
        label="Website"
        type="url"
        placeholder="https://www.fornecedor.com.br"
      />

      <FormField
        control={form.control}
        name="notes"
        render={({ field }) => (
          <FormItem>
            <FormLabel>Observações</FormLabel>
            <FormControl>
              <Textarea
                placeholder="Anotações internas sobre o fornecedor"
                className="resize-none"
                rows={3}
                value={field.value ?? ""}
                onChange={field.onChange}
                onBlur={field.onBlur}
                name={field.name}
                ref={field.ref}
              />
            </FormControl>
            <FormMessage />
          </FormItem>
        )}
      />
    </FormDialog>
  );
}
