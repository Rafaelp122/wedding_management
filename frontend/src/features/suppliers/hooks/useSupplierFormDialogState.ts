import { useState } from "react";

import type { SupplierOut } from "@/api/generated/v1/models";
import {
  EMPTY_SUPPLIER_FORM_STATE,
  type SupplierFormMode,
  type SupplierFormState,
} from "../types";

export function useSupplierFormDialogState() {
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<SupplierFormMode>("create");
  const [formState, setFormState] = useState<SupplierFormState>({
    ...EMPTY_SUPPLIER_FORM_STATE,
  });

  const openCreateDialog = () => {
    setFormMode("create");
    setFormState({ ...EMPTY_SUPPLIER_FORM_STATE });
    setFormOpen(true);
  };

  const openEditDialog = (supplier: SupplierOut) => {
    setFormMode("edit");
    setFormState({
      uuid: supplier.uuid,
      name: supplier.name,
      cnpj: supplier.cnpj,
      phone: supplier.phone,
      email: supplier.email,
      status: supplier.is_active ? "active" : "inactive",
    });
    setFormOpen(true);
  };

  return {
    formOpen,
    setFormOpen,
    formMode,
    formState,
    setFormState,
    openCreateDialog,
    openEditDialog,
  };
}
