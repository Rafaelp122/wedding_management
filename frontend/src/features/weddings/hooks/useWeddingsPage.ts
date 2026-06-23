import { useEffect, useMemo, useState } from "react";

import { useWeddingsList } from "@/api/generated/v1/endpoints/weddings/weddings";
import {
  getPaginationInfo,
  usePagination,
} from "@/hooks/use-pagination";
import { useDebounce } from "@/hooks/use-debounce";

import type { WeddingStatusFilter } from "@/features/weddings/utils/wedding-status";

export const WEDDINGS_PAGE_SIZE = 5;

export function useWeddingsPage() {
  const [search, setSearch] = useState("");
  const debouncedSearch = useDebounce(search, 300);
  const [statusFilter, setStatusFilter] = useState<WeddingStatusFilter>("all");
  const [createDialogOpen, setCreateDialogOpen] = useState(false);

  const pagination = usePagination(WEDDINGS_PAGE_SIZE);

  const {
    data: weddingsResponse,
    isLoading,
    isFetching,
    error,
    refetch,
  } = useWeddingsList(
    {
      limit: pagination.limit,
      offset: pagination.offset,
      search: debouncedSearch || undefined,
      status: statusFilter !== "all" ? statusFilter : undefined,
    },
    {
      query: {
        placeholderData: (previousData) => previousData,
      },
    },
  );

  const weddings = useMemo(
    () => weddingsResponse?.data.items ?? [],
    [weddingsResponse],
  );
  const totalCount = weddingsResponse?.data.count ?? 0;

  const paginationInfo = getPaginationInfo(
    pagination.page,
    pagination.pageSize,
    totalCount,
  );

  useEffect(() => {
    pagination.resetPage();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch, statusFilter]);

  return {
    search,
    setSearch,
    statusFilter,
    setStatusFilter,
    createDialogOpen,
    setCreateDialogOpen,
    filteredWeddings: weddings,
    totalCount,
    isLoading,
    isFetching,
    error,
    refetch,
    pagination: {
      ...pagination,
      info: paginationInfo,
      pageSize: WEDDINGS_PAGE_SIZE,
    },
  };
}
