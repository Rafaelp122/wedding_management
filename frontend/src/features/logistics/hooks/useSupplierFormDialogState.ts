import { useState } from "react";

import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import type { SupplierFormMode } from "../types";

export function useSupplierFormDialogState() {
  const [formOpen, setFormOpen] = useState(false);
  const [formMode, setFormMode] = useState<SupplierFormMode>("create");
  const [editingSupplier, setEditingSupplier] = useState<SupplierOut | null>(null);

  const openCreateDialog = () => {
    setFormMode("create");
    setEditingSupplier(null);
    setFormOpen(true);
  };

  const openEditDialog = (supplier: SupplierOut) => {
    setFormMode("edit");
    setEditingSupplier(supplier);
    setFormOpen(true);
  };

  return {
    formOpen,
    setFormOpen,
    formMode,
    editingSupplier,
    openCreateDialog,
    openEditDialog,
  };
}
