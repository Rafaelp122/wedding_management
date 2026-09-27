import { memo } from "react";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";

import {
  useContractsAddendumsSign,
  getContractsListQueryKey,
  getContractsDetailsReadQueryKey,
  getContractsReadQueryKey,
  getContractsAddendumsListQueryKey,
} from "@/api/generated/v1/endpoints/contracts/contracts";
import { getApiErrorInfo } from "@/api/error-utils";
import type { ContractAddendumOut } from "@/api/generated/v1/models/contractAddendumOut";
import { SignAddendumDialogView } from "./SignAddendumDialogView";

export interface SignAddendumDialogProps {
  contractUuid: string;
  addendum: ContractAddendumOut | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export const SignAddendumDialog = memo(function SignAddendumDialog({
  contractUuid,
  addendum,
  open,
  onOpenChange,
  onSuccess,
}: SignAddendumDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useContractsAddendumsSign();

  const handleConfirm = (signedDate: string) => {
    if (!addendum || !contractUuid) return;
    mutate(
      {
        contractId: contractUuid,
        addendumId: addendum.uuid,
        data: {
          signed_date: signedDate,
        },
      },
      {
        onSuccess: () => {
          toast.success("Aditivo assinado com sucesso!");
          queryClient.invalidateQueries({
            queryKey: getContractsListQueryKey(),
          });
          queryClient.invalidateQueries({
            queryKey: getContractsDetailsReadQueryKey(contractUuid),
          });
          queryClient.invalidateQueries({
            queryKey: getContractsReadQueryKey(contractUuid),
          });
          queryClient.invalidateQueries({
            queryKey: getContractsAddendumsListQueryKey(contractUuid),
          });
          onOpenChange(false);
          onSuccess?.();
        },
        onError: (error) => {
          const { message } = getApiErrorInfo(
            error,
            "Erro ao formalizar assinatura do aditivo.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <SignAddendumDialogView
      addendum={addendum}
      open={open}
      onOpenChange={onOpenChange}
      onConfirm={handleConfirm}
      isPending={isPending}
    />
  );
});
