import type { Dispatch, SetStateAction } from "react";
import { toast } from "sonner";

import {
  useLogisticsSuppliersCreate,
  useLogisticsSuppliersDelete,
  useLogisticsSuppliersUpdate,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { getApiErrorInfo } from "@/api/error-utils";

import type { SupplierFormMode, SupplierFormState } from "../types";
import {
  buildSupplierPayload,
  getSupplierFormValidationMessage,
} from "../utils/supplierForm";

interface UseSupplierMutationsParams {
  formMode: SupplierFormMode;
  formState: SupplierFormState;
  supplierToDelete: SupplierOut | null;
  setFormOpen: Dispatch<SetStateAction<boolean>>;
  setSupplierToDelete: Dispatch<SetStateAction<SupplierOut | null>>;
  refetchSuppliers: () => Promise<unknown>;
}

export function useSupplierMutations({
  formMode,
  formState,
  supplierToDelete,
  setFormOpen,
  setSupplierToDelete,
  refetchSuppliers,
}: UseSupplierMutationsParams) {
  const createSupplierMutation = useLogisticsSuppliersCreate();
  const updateSupplierMutation = useLogisticsSuppliersUpdate();
  const deleteSupplierMutation = useLogisticsSuppliersDelete();

  const handleSaveSupplier = async () => {
    const validationMessage = getSupplierFormValidationMessage(formState);
    if (validationMessage) {
      toast.error(validationMessage);
      return;
    }

    const payload = buildSupplierPayload(formState);

    try {
      if (formMode === "create") {
        await createSupplierMutation.mutateAsync({ data: payload });
        toast.success("Fornecedor criado com sucesso!");
      } else {
        if (!formState.uuid) {
          toast.error("Fornecedor inválido para edição.");
          return;
        }

        await updateSupplierMutation.mutateAsync({
          uuid: formState.uuid,
          data: payload,
        });
        toast.success("Fornecedor atualizado com sucesso!");
      }

      setFormOpen(false);
      await refetchSuppliers();
    } catch (mutationError) {
      const { message } = getApiErrorInfo(
        mutationError,
        "Não foi possível salvar o fornecedor.",
      );
      toast.error(message);
    }
  };

  const handleDeleteSupplier = async () => {
    if (!supplierToDelete) {
      return;
    }

    try {
      await deleteSupplierMutation.mutateAsync({ uuid: supplierToDelete.uuid });
      toast.success("Fornecedor removido com sucesso!");
      setSupplierToDelete(null);
      await refetchSuppliers();
    } catch (mutationError) {
      const { message } = getApiErrorInfo(
        mutationError,
        "Não foi possível remover o fornecedor.",
      );
      toast.error(message);
    }
  };

  return {
    handleSaveSupplier,
    handleDeleteSupplier,
    isSaving:
      createSupplierMutation.isPending || updateSupplierMutation.isPending,
    isDeleting: deleteSupplierMutation.isPending,
  };
}
