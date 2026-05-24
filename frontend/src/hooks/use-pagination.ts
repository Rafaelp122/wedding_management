import { useState, useCallback } from "react";

export interface PaginationInfo {
  page: number;
  pageSize: number;
  totalPages: number;
  totalCount: number;
  hasPrevious: boolean;
  hasNext: boolean;
  from: number;
  to: number;
}

export function getPaginationInfo(
  page: number,
  pageSize: number,
  totalCount: number,
): PaginationInfo {
  const totalPages = Math.max(1, Math.ceil(totalCount / pageSize));
  const safePage = Math.min(page, totalPages);

  return {
    page: safePage,
    pageSize,
    totalPages,
    totalCount,
    hasPrevious: safePage > 1,
    hasNext: safePage < totalPages,
    from: totalCount === 0 ? 0 : (safePage - 1) * pageSize + 1,
    to: Math.min(safePage * pageSize, totalCount),
  };
}

export function usePagination(defaultPageSize = 10) {
  const [page, setPage] = useState(1);
  const [pageSize] = useState(defaultPageSize);

  const offset = (page - 1) * pageSize;

  const goToPage = useCallback((p: number) => setPage(Math.max(1, p)), []);
  const previousPage = useCallback(
    () => setPage((p) => Math.max(1, p - 1)),
    [],
  );
  const nextPage = useCallback(() => setPage((p) => p + 1), []);
  const firstPage = useCallback(() => setPage(1), []);
  const resetPage = useCallback(() => setPage(1), []);

  return {
    page,
    pageSize,
    limit: pageSize,
    offset,
    goToPage,
    previousPage,
    nextPage,
    firstPage,
    resetPage,
  };
}
