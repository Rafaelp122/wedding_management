import { memo } from "react";

import {
  useContractsUpdate,
  useContractsList,
} from "@/api/generated/v1/endpoints/contracts/contracts";
import { useSuppliersList } from "@/api/generated/v1/endpoints/suppliers/suppliers";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import type { ContractPatchIn } from "@/api/generated/v1/models/contractPatchIn";

import { CONTRACT_STATUS_OPTIONS } from "@/features/contracts/constants";
import { buildPatchPayload } from "@/lib/patch-payload";
import {
  EditContractDialogView,
  type EditContractFormData,
} from "./EditContractDialogView";

interface EditContractDialogProps {
  contract: ContractOut;
  weddingUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const EditContractDialog = memo(function EditContractDialog({
  contract,
  weddingUuid,
  open,
  onOpenChange,
  onSuccess,
}: EditContractDialogProps) {
  const { mutate, isPending } = useContractsUpdate();

  const { data: suppliersResponse } = useSuppliersList();
  const suppliers = suppliersResponse?.data?.items ?? [];

  const { data: contractsResponse } = useContractsList({
    wedding_id: weddingUuid,
  });
  const existingContracts =
    contractsResponse?.data?.items?.filter((c) => c.uuid !== contract.uuid) ?? [];

  const allowedSet = new Set([
    contract.status,
    ...(contract.allowed_transitions ?? []),
  ]);
  const availableStatusOptions = CONTRACT_STATUS_OPTIONS.filter((opt) =>
    allowedSet.has(opt.value),
  );

  const onSubmit = (data: EditContractFormData) => {
    const original: Record<string, unknown> = {
      supplier: contract.supplier,
      name: contract.name || "",
      total_amount: Number(contract.total_amount),
      status: contract.status,
      description: contract.description || "",
      parent: contract.parent ?? null,
    };
    const modified: Record<string, unknown> = {
      supplier: data.supplier,
      name: data.name,
      total_amount: data.total_amount,
      status: data.status,
      description: data.description,
      parent: data.parent ?? null,
    };

    const payload = buildPatchPayload(original, modified, [
      "supplier",
      "name",
      "total_amount",
      "status",
      "description",
      "parent",
    ]);

    if (Object.keys(payload).length === 0) {
      onOpenChange(false);
      return;
    }

    mutate(
      { uuid: contract.uuid, data: payload as ContractPatchIn },
      createMutationCallbacks({
        successMsg: "Contrato atualizado com sucesso!",
        fallbackErrorMsg: "Erro ao atualizar contrato.",
        onSuccess: () => onSuccess(),
      }),
    );
  };

  return (
    <EditContractDialogView
      contract={contract}
      open={open}
      onOpenChange={onOpenChange}
      onSubmit={onSubmit}
      isPending={isPending}
      suppliers={suppliers}
      existingContracts={existingContracts}
      availableStatusOptions={availableStatusOptions}
    />
  );
});
