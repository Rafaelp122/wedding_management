import { memo } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import {
  useContractsAddendumsCreate,
  getContractsListQueryKey,
  getContractsDetailsReadQueryKey,
  getContractsReadQueryKey,
  getContractsAddendumsListQueryKey,
} from "@/api/generated/v1/endpoints/contracts/contracts";
import { getApiErrorInfo } from "@/api/error-utils";
import {
  CreateAddendumDialogView,
  type CreateAddendumFormData,
} from "./CreateAddendumDialogView";

export type { CreateAddendumFormData };

export interface CreateAddendumDialogProps {
  contractUuid: string;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSuccess?: () => void;
}

export const CreateAddendumDialog = memo(function CreateAddendumDialog({
  contractUuid,
  open,
  onOpenChange,
  onSuccess,
}: CreateAddendumDialogProps) {
  const queryClient = useQueryClient();
  const { mutate, isPending } = useContractsAddendumsCreate();

  const handleSubmit = (data: CreateAddendumFormData) => {
    mutate(
      {
        contractId: contractUuid,
        data: {
          amount: data.amount,
          justification: data.justification,
        },
      },
      {
        onSuccess: () => {
          toast.success("Termo aditivo criado com sucesso!");
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
            "Erro ao criar termo aditivo.",
          );
          toast.error(message);
        },
      },
    );
  };

  return (
    <CreateAddendumDialogView
      open={open}
      onOpenChange={onOpenChange}
      onSubmit={handleSubmit}
      isPending={isPending}
    />
  );
});
