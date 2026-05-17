import type { Dispatch, SetStateAction } from "react";

import {
  useLogisticsSuppliersDelete,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";

interface UseSupplierMutationsParams {
  supplierToDelete: SupplierOut | null;
  setSupplierToDelete: Dispatch<SetStateAction<SupplierOut | null>>;
  refetchSuppliers: () => Promise<unknown>;
}

export function useSupplierMutations({
  supplierToDelete,
  setSupplierToDelete,
  refetchSuppliers,
}: UseSupplierMutationsParams) {
  const deleteSupplierMutation = useLogisticsSuppliersDelete();

  const handleDeleteSupplier = () => {
    if (!supplierToDelete) return;

    deleteSupplierMutation.mutate(
      { uuid: supplierToDelete.uuid },
      createMutationCallbacks({
        successMsg: "Fornecedor removido com sucesso!",
        fallbackErrorMsg: "Não foi possível remover o fornecedor.",
        onSuccess: () => {
          setSupplierToDelete(null);
          refetchSuppliers();
        },
      }),
    );
  };

  return {
    handleDeleteSupplier,
    isDeleting: deleteSupplierMutation.isPending,
  };
}
