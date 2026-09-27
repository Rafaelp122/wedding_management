import { memo } from "react";

import {
  useLogisticsItemsUpdate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { useContractsList } from "@/api/generated/v1/endpoints/contracts/contracts";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { ItemOut } from "@/api/generated/v1/models/itemOut";
import type { ItemPatchIn } from "@/api/generated/v1/models/itemPatchIn";

import { buildPatchPayload } from "@/lib/patch-payload";
import {
  EditItemDialogView,
  type EditItemFormData,
} from "./EditItemDialogView";

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

  const { data: contractsResponse } = useContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items ?? [];

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
    <EditItemDialogView
      item={item}
      open={open}
      onOpenChange={onOpenChange}
      onSubmit={onSubmit}
      isPending={isPending}
      contracts={contracts}
    />
  );
});
