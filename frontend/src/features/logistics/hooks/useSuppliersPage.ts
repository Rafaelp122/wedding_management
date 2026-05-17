import { useDeferredValue, useMemo, useState } from "react";

import {
  useLogisticsSuppliersList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";

import { useSupplierFilters } from "./useSupplierFilters";
import { useSupplierFormDialogState } from "./useSupplierFormDialogState";
import { useSupplierMutations } from "./useSupplierMutations";
import type { SupplierStatusFilter } from "../types";

export function useSuppliersPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<SupplierStatusFilter>("all");
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierOut | null>(null);
  const deferredSearch = useDeferredValue(search);

  const {
    data: suppliersResponse,
    isLoading,
    error,
    refetch,
  } = useLogisticsSuppliersList({ limit: 300 });

  const suppliers = useMemo(
    () => suppliersResponse?.data.items ?? [],
    [suppliersResponse],
  );
  const totalCount = suppliersResponse?.data.count ?? 0;

  const filteredSuppliers = useSupplierFilters(suppliers, deferredSearch, statusFilter);

  const {
    formOpen,
    setFormOpen,
    formMode,
    editingSupplier,
    openCreateDialog,
    openEditDialog,
  } = useSupplierFormDialogState();

  const { handleDeleteSupplier, isDeleting } = useSupplierMutations({
    supplierToDelete,
    setSupplierToDelete,
    refetchSuppliers: () => refetch(),
  });

  return {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    formOpen,
    setFormOpen,
    formMode,
    editingSupplier,
    supplierToDelete,
    setSupplierToDelete,
    filteredSuppliers,
    totalCount,
    isLoading,
    error,
    refetch,
    isDeleting,
    openCreateDialog,
    openEditDialog,
    handleDeleteSupplier,
  };
}
