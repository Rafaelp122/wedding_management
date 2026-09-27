import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import { LogisticsItemsUpdateBody } from "@/api/generated/v1/zod/logistics/logistics";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";
import { ACQUISITION_STATUS_OPTIONS } from "@/features/logistics/constants";

export type EditItemFormData = z.input<typeof LogisticsItemsUpdateBody>;

export interface EditItemDialogViewProps {
  item: ItemOut;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (data: EditItemFormData) => void;
  isPending: boolean;
  contracts: ContractOut[];
}

export const EditItemDialogView = memo(function EditItemDialogView({
  item,
  open,
  onOpenChange,
  onSubmit,
  isPending,
  contracts,
}: EditItemDialogViewProps) {
  const form = useForm<EditItemFormData>({
    resolver: zodResolver(LogisticsItemsUpdateBody),
    defaultValues: {
      name: item.name,
      description: item.description || "",
      quantity: item.quantity,
      contract: item.contract ?? null,
      acquisition_status: item.acquisition_status,
    },
  });

  return (
    <FormDialog
      open={open}
      onOpenChange={onOpenChange}
      title="Editar Item"
      description="Altere as informações do item logístico."
      form={form}
      onSubmit={form.handleSubmit(onSubmit)}
      isPending={isPending}
      submitLabel="Salvar"
      maxWidth="480px"
    >
      <FormInput
        control={form.control}
        name="name"
        label="Nome"
      />

      <FormTextarea
        control={form.control}
        name="description"
        label="Descrição"
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
          name="acquisition_status"
          label="Status"
          items={ACQUISITION_STATUS_OPTIONS}
          getItemKey={(opt) => opt.value}
          getItemLabel={(opt) => opt.label}
          placeholder="Status"
        />
      </div>

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
    </FormDialog>
  );
});
