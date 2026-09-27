import { memo } from "react";
import { useForm, type Resolver } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { LogisticsItemsCreateBody } from "@/api/generated/v1/zod/logistics/logistics";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";
import { ACQUISITION_STATUS_OPTIONS, INITIAL_SCOPE_OPTIONS } from "@/features/logistics/constants";

export type CreateItemFormData = z.input<typeof LogisticsItemsCreateBody>;

export interface CreateItemDialogViewProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: CreateItemFormData, onDone: () => void) => void;
  isPending: boolean;
  contracts: ContractOut[];
}

export const CreateItemDialogView = memo(function CreateItemDialogView({
  weddingUuid,
  open,
  onOpenChange,
  onSubmit,
  isPending,
  contracts,
}: CreateItemDialogViewProps) {
  const form = useForm<CreateItemFormData>({
    resolver: zodResolver(LogisticsItemsCreateBody) as Resolver<CreateItemFormData>,
    defaultValues: {
      wedding: weddingUuid,
      contract: null,
      name: "",
      description: "",
      quantity: 1,
      scope_status: "INCLUDED",
      acquisition_status: "PENDING",
    },
  });

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Novo Item"
      description="Registre um item logístico vinculado ao evento."
      form={form}
      onSubmit={form.handleSubmit((data) => onSubmit(data, () => form.reset()))}
      isPending={isPending}
      submitLabel="Criar Item"
      maxWidth="480px"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
        placeholder="Ex: Buquê de rosas"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição (Opcional)"
        placeholder="Detalhes do item..."
      />

      <div className="grid grid-cols-2 gap-4">
        <FormNumber
          control={form.control}
          name="quantity"
          label="Quantidade"
          step="1"
          min={1}
          transformEmptyTo={1}
        />

        <FormSelect
          control={form.control}
          name="scope_status"
          label="Escopo Inicial"
          items={INITIAL_SCOPE_OPTIONS}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
          placeholder="Escopo"
        />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <FormSelect
          control={form.control}
          name="acquisition_status"
          label="Status"
          items={ACQUISITION_STATUS_OPTIONS}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
          placeholder="Status"
        />

        <FormSelectNullable
          control={form.control}
          name="contract"
          label="Contrato (Opcional)"
          items={contracts}
          getItemKey={(c) => c.uuid}
          getItemLabel={(c) =>
            c.supplier_name || c.description || c.uuid.substring(0, 8)
          }
          placeholder="Nenhum contrato"
        />
      </div>
    </FormDialog>
  );
});
