import { describe, expect, it } from "vitest";
import { act, renderHook } from "@/test-utils";
import { getPaginationInfo, usePagination } from "@/hooks/use-pagination";

describe("usePagination", () => {
  it("starts at page 1 with default page size 10", () => {
    const { result } = renderHook(() => usePagination());

    expect(result.current.page).toBe(1);
    expect(result.current.pageSize).toBe(10);
    expect(result.current.limit).toBe(10);
    expect(result.current.offset).toBe(0);
  });

  it("uses custom defaultPageSize", () => {
    const { result } = renderHook(() => usePagination(25));

    expect(result.current.pageSize).toBe(25);
    expect(result.current.limit).toBe(25);
    expect(result.current.offset).toBe(0);
  });

  it("nextPage increments page", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.nextPage();
    });

    expect(result.current.page).toBe(2);
    expect(result.current.offset).toBe(10);
  });

  it("previousPage does not go below 1", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.previousPage();
    });

    expect(result.current.page).toBe(1);
  });

  it("previousPage decrements page from higher value", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.nextPage();
      result.current.nextPage();
    });
    expect(result.current.page).toBe(3);

    act(() => {
      result.current.previousPage();
    });
    expect(result.current.page).toBe(2);
  });

  it("goToPage sets a specific page", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.goToPage(5);
    });

    expect(result.current.page).toBe(5);
    expect(result.current.offset).toBe(40);
  });

  it("goToPage does not go below 1", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.goToPage(0);
    });

    expect(result.current.page).toBe(1);
  });

  it("resetPage goes back to page 1", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.goToPage(7);
    });
    expect(result.current.page).toBe(7);

    act(() => {
      result.current.resetPage();
    });
    expect(result.current.page).toBe(1);
  });

  it("firstPage goes to page 1", () => {
    const { result } = renderHook(() => usePagination());

    act(() => {
      result.current.nextPage();
      result.current.nextPage();
    });

    act(() => {
      result.current.firstPage();
    });
    expect(result.current.page).toBe(1);
  });
});

describe("getPaginationInfo", () => {
  it("calculates correct info for page 1 of 50 items", () => {
    const info = getPaginationInfo(1, 10, 50);

    expect(info.page).toBe(1);
    expect(info.totalPages).toBe(5);
    expect(info.totalCount).toBe(50);
    expect(info.hasPrevious).toBe(false);
    expect(info.hasNext).toBe(true);
    expect(info.from).toBe(1);
    expect(info.to).toBe(10);
  });

  it("calculates correct info for last partial page", () => {
    const info = getPaginationInfo(5, 10, 50);

    expect(info.page).toBe(5);
    expect(info.totalPages).toBe(5);
    expect(info.hasPrevious).toBe(true);
    expect(info.hasNext).toBe(false);
    expect(info.from).toBe(41);
    expect(info.to).toBe(50);
  });

  it("calculates correct info for partial last page", () => {
    const info = getPaginationInfo(2, 10, 15);

    expect(info.totalPages).toBe(2);
    expect(info.hasPrevious).toBe(true);
    expect(info.hasNext).toBe(false);
    expect(info.from).toBe(11);
    expect(info.to).toBe(15);
  });

  it("returns empty info for zero items", () => {
    const info = getPaginationInfo(1, 10, 0);

    expect(info.totalPages).toBe(1);
    expect(info.hasPrevious).toBe(false);
    expect(info.hasNext).toBe(false);
    expect(info.from).toBe(0);
    expect(info.to).toBe(0);
  });

  it("caps page to totalPages when page exceeds total pages", () => {
    const info = getPaginationInfo(10, 10, 50);

    expect(info.page).toBe(5);
    expect(info.totalPages).toBe(5);
  });
});
