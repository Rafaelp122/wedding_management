import { memo } from "react";
import { toast } from "sonner";

import { useContractsSign } from "@/api/generated/v1/endpoints/contracts/contracts";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ContractOut } from "@/api/generated/v1/models/contractOut";
import { SignContractDialogView } from "./SignContractDialogView";

interface SignContractDialogProps {
  contract: ContractOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess: () => void;
}

export const SignContractDialog = memo(function SignContractDialog({
  contract,
  open,
  onOpenChange,
  onSuccess,
}: SignContractDialogProps) {
  const { mutate, isPending } = useContractsSign();

  const handleConfirm = (signedDate: string) => {
    if (!contract) return;
    mutate(
      {
        uuid: contract.uuid,
        data: {
          signed_date: signedDate,
        },
      },
      {
        onSuccess: () => {
          toast.success("Contrato assinado formalmente com sucesso!");
          onOpenChange(false);
          onSuccess();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(error, "Erro ao formalizar assinatura do contrato.");
          toast.error(message);
        },
      },
    );
  };

  return (
    <SignContractDialogView
      contract={contract}
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      isPending={isPending}
    />
  );
});
