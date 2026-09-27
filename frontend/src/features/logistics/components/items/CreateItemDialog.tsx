import { memo } from "react";

import {
  useLogisticsItemsCreate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import { useContractsList } from "@/api/generated/v1/endpoints/contracts/contracts";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import {
  CreateItemDialogView,
  type CreateItemFormData,
} from "./CreateItemDialogView";

interface CreateItemDialogProps {
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const CreateItemDialog = memo(function CreateItemDialog({
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateItemDialogProps) {
  const { mutate, isPending } = useLogisticsItemsCreate();

  const { data: contractsResponse } = useContractsList({
    wedding_id: weddingUuid,
  });
  const contracts = contractsResponse?.data?.items ?? [];

  const onSubmit = (data: CreateItemFormData, onDone: () => void) => {
    mutate(
      { data },
      createMutationCallbacks({
        successMsg: "Item criado com sucesso!",
        fallbackErrorMsg: "Erro ao criar item.",
        onSuccess: () => {
          onDone();
          onSuccess();
        },
      }),
    );
  };

  return (
    <CreateItemDialogView
      weddingUuid={weddingUuid}
      open={open}
      onOpenChange={onOpenChange}
      onSubmit={onSubmit}
      isPending={isPending}
      contracts={contracts}
    />
  );
});
