import {
  useSuppliersCreate,
  useSuppliersUpdate,
} from "@/api/generated/v1/endpoints/suppliers/suppliers";
import { createMutationCallbacks } from "@/hooks/use-mutation-toast";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";

import type { SupplierFormData } from "@/features/logistics/hooks/supplierFormSchema";
import { SupplierFormDialogView } from "./SupplierFormDialogView";

interface SupplierFormDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  mode: "create" | "edit";
  supplier: SupplierOut | null;
  onSuccess: () => void;
}

export function SupplierFormDialog({
  open,
  onOpenChange,
  mode,
  supplier,
  onSuccess,
}: SupplierFormDialogProps) {
  const createMutation = useSuppliersCreate();
  const updateMutation = useSuppliersUpdate();
  const isPending = mode === "create" ? createMutation.isPending : updateMutation.isPending;

  const onSubmit = (data: SupplierFormData) => {
    if (mode === "create") {
      createMutation.mutate(
        { data },
        createMutationCallbacks({
          successMsg: "Fornecedor criado com sucesso!",
          fallbackErrorMsg: "Não foi possível salvar o fornecedor.",
          onSuccess: () => {
            onSuccess();
          },
        }),
      );
    } else if (supplier) {
      updateMutation.mutate(
        { uuid: supplier.uuid, data },
        createMutationCallbacks({
          successMsg: "Fornecedor atualizado com sucesso!",
          fallbackErrorMsg: "Não foi possível salvar o fornecedor.",
          onSuccess: () => onSuccess(),
        }),
      );
    }
  };

  return (
    <SupplierFormDialogView
      open={open}
      onOpenChange={onOpenChange}
      mode={mode}
      supplier={supplier}
      onSubmit={onSubmit}
      isPending={isPending}
    />
  );
}
