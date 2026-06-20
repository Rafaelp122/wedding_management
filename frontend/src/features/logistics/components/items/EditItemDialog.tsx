import { memo } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import type { z } from "zod";

import {
  useLogisticsItemsUpdate,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { LogisticsItemsUpdateBody } from "@/api/generated/v1/zod/logistics/logistics";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import type { ItemPatchIn } from "@/api/generated/v1/models/itemPatchIn";

import { FormDialog } from "@/components/form-dialog";
import { FormInput, FormSelect, FormSelectNullable, FormNumber, FormTextarea } from "@/components/form-fields";
import { ACQUISITION_STATUS_OPTIONS } from "@/features/logistics/constants";
import { buildPatchPayload } from "@/lib/patch-payload";

type EditItemFormData = z.input<typeof LogisticsItemsUpdateBody>;

interface EditItemDialogProps {
  item: ItemOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const EditItemDialog = memo(function EditItemDialog({
  item,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditItemDialogProps) {
  const { mutate, isPending } = useLogisticsItemsUpdate();

  const { data: contractsResponse } = useLogisticsContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items ?? [];

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

  const onSubmit = (data: EditItemFormData) => {
    const original: Record<string, unknown> = {
      name: item.name,
      description: item.description || "",
      quantity: item.quantity,
      contract: item.contract ?? null,
      acquisition_status: item.acquisition_status,
    };
    const modified: Record<string, unknown> = {
      name: data.name,
      description: data.description,
      quantity: data.quantity,
      contract: data.contract,
      acquisition_status: data.acquisition_status,
    };

    const payload = buildPatchPayload(original, modified, [
      "name",
      "description",
      "quantity",
      "contract",
      "acquisition_status",
    ]);

    if (Object.keys(payload).length === 0) {
      onOpenChange(false);
      return;
    }

    mutate(
      { uuid: item.uuid, data: payload as ItemPatchIn },
      createMutationCallbacks({
        successMsg: "Item atualizado com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar item.",
        onSuccess: () => onSuccess(),
      }),
    );
  };

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
