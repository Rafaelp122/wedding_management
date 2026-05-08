import { useMemo } from "react";

import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import type { SupplierStatusFilter } from "../types";

export function useSupplierFilters(
  suppliers: SupplierOut[],
  search: string,
  statusFilter: SupplierStatusFilter,
) {
  return useMemo(() => {
    return suppliers.filter((supplier) => {
      const matchesSearch =
        search === "" ||
        supplier.name.toLowerCase().includes(search.toLowerCase()) ||
        supplier.email.toLowerCase().includes(search.toLowerCase()) ||
        supplier.phone.toLowerCase().includes(search.toLowerCase()) ||
        supplier.cnpj.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" ||
        (statusFilter === "active" && supplier.is_active) ||
        (statusFilter === "inactive" && !supplier.is_active);

      return matchesSearch && matchesStatus;
    });
  }, [suppliers, search, statusFilter]);
}
