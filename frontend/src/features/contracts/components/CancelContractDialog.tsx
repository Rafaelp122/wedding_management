import { memo } from "react";
import { toast } from "sonner";

import { useContractsStatusTransition } from "@/api/generated/v1/endpoints/contracts/contracts";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { CancelContractDialogView } from "./CancelContractDialogView";

interface CancelContractDialogProps {
  contract: ContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const CancelContractDialog = memo(function CancelContractDialog({
  contract,
  open,
  onOpenChange,
  onSuccess,
}: CancelContractDialogProps) {
  const { mutate, isPending } = useContractsStatusTransition();

  const handleConfirm = () => {
    if (!contract) return;
    mutate(
      {
        uuid: contract.uuid,
        data: {
          status: "CANCELED",
        },
      },
      {
        onSuccess: () => {
          toast.success("Contrato cancelado com sucesso!");
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao cancelar contrato.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <CancelContractDialogView
      contract={contract}
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      isPending={isPending}
    />
  );
});
