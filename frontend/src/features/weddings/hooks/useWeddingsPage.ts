import { useMemo, useState } from "react";

import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";

import { useWeddingFilters } from "./useWeddingFilters";
import type { WeddingStatusFilter } from "../utils/weddingStatus";

export function useWeddingsPage() {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState<WeddingStatusFilter>("all");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const {
    data: weddingsResponse,
    isLoading,
    error,
    refetch,
  } = useWeddingsList();

  const weddings = useMemo(
    () => weddingsResponse?.data.items ?? [],
    [weddingsResponse],
  );
  const totalCount = weddingsResponse?.data.count ?? 0;

  const filteredWeddings = useWeddingFilters(weddings, search, statusFilter);

  return {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    createDialogOpen,
    setCreateDialogOpen,
    filteredWeddings,
    totalCount,
    isLoading,
    error,
    refetch,
  };
}
