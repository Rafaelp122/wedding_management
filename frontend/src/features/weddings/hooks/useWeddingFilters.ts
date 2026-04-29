import { useMemo } from "react";

import type { WeddingOut } from "@/api/generated/v1/models";
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
        wedding.wedding_detail?.groom_name.toLowerCase().includes(search.toLowerCase()) ||
        wedding.wedding_detail?.bride_name.toLowerCase().includes(search.toLowerCase()) ||
        wedding.location.toLowerCase().includes(search.toLowerCase());

      const matchesStatus =
        statusFilter === "all" || wedding.status === statusFilter;

      return matchesSearch && matchesStatus;
    });
  }, [weddings, search, statusFilter]);
}
