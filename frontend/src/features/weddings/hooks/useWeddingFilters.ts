import { useMemo } from "react";

import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { WeddingStatusFilter } from "../utils/weddingStatus";

export function useWeddingFilters(
  weddings: WeddingOut[],
  search: string,
  statusFilter: WeddingStatusFilter,
) {
  return useMemo(() => {
    return weddings.filter((wedding) => {
      const matchesSearch =
        search === "" ||
        wedding.groom_name.toLowerCase().includes(search.toLowerCase()) ||
        wedding.bride_name.toLowerCase().includes(search.toLowerCase()) ||
        wedding.location.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" || wedding.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [weddings, search, statusFilter]);
}
