import { toast } from "sonner";

import { getApiErrorInfo } from "@/api/error-utils";

interface MutationToastOptions<TData> {
  successMsg: string;
  fallbackErrorMsg?: string;
  onSuccess?: (data: TData) => void;
}

export function createMutationCallbacks<TData = unknown>({
  successMsg,
  fallbackErrorMsg = "Não foi possível concluir a operação.",
  onSuccess,
}: MutationToastOptions<TData>) {
  return {
    onSuccess: (data: TData) => {
      toast.success(successMsg);
      onSuccess?.(data);
    },
    onError: (error: unknown) => {
      const { message } = getApiErrorInfo(error, fallbackErrorMsg);
      toast.error(message);
    },
  };
}
