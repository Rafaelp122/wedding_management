import { useEffect, useMemo, useState } from "react";

import {
  useLogisticsSuppliersList,
} from "@/api/generated/v1/endpoints/logistics/logistics";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import {
  getPaginationInfo,
  usePagination,
} from "@/hooks/use-pagination";

import { useSupplierFormDialogState } from "./useSupplierFormDialogState";
import { useSupplierMutations } from "./useSupplierMutations";
import type { SupplierStatusFilter } from "../types";

export function useSuppliersPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<SupplierStatusFilter>("all");
  const [supplierToDelete, setSupplierToDelete] = useState<SupplierOut | null>(null);

  const pagination = usePagination();

  const isActiveParam =
    statusFilter === "all" ? undefined : statusFilter === "active";

  const {
    data: suppliersResponse,
    isLoading,
    isFetching,
    error,
    refetch,
  } = useLogisticsSuppliersList(
    {
      limit: pagination.limit,
      offset: pagination.offset,
      search: search || undefined,
      is_active: isActiveParam,
    },
    {
      query: {
        placeholderData: (previousData) => previousData,
      },
    },
  );

  const suppliers = useMemo(
    () => suppliersResponse?.data.items ?? [],
    [suppliersResponse],
  );
  const totalCount = suppliersResponse?.data.count ?? 0;

  const paginationInfo = getPaginationInfo(
    pagination.page,
    pagination.pageSize,
    totalCount,
  );

  useEffect(() => {
    pagination.resetPage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [search, statusFilter]);

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
    filteredSuppliers: suppliers,
    totalCount,
    isLoading,
    isFetching,
    error,
    refetch,
    isDeleting,
    openCreateDialog,
    openEditDialog,
    handleDeleteSupplier,
    pagination: {
      ...pagination,
      info: paginationInfo,
    },
  };
}
