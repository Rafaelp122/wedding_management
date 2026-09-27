import { memo } from "react";

import { useSuppliersRead } from "@/api/generated/v1/endpoints/suppliers/suppliers";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { SupplierDetailDialogView } from "./SupplierDetailDialogView";

interface SupplierDetailDialogProps {
  supplierUuid: string | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export const SupplierDetailDialog = memo(function SupplierDetailDialog({
  supplierUuid,
  open,
  onOpenChange,
}: SupplierDetailDialogProps) {
  const { data: response, isLoading, error } = useSuppliersRead(
    supplierUuid ?? "",
    { query: { enabled: !!supplierUuid } },
  );

  const supplier: SupplierOut | undefined = response?.data;

  return (
    <SupplierDetailDialogView
      supplier={supplier}
      isLoading={isLoading}
      error={error}
      open={open}
      onOpenChange={onOpenChange}
    />
  );
});
