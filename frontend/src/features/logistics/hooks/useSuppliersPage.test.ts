import { describe, expect, it } from "vitest";
import { renderHook, waitFor, act } from "@/test-utils";
import { useSuppliersPage } from "@/features/logistics/hooks/useSuppliersPage";

describe("useSuppliersPage", () => {
  it("initializes with default values", () => {
    const { result } = renderHook(() => useSuppliersPage());

    expect(result.current.search).toBe("");
    expect(result.current.statusFilter).toBe("all");
    expect(result.current.formOpen).toBe(false);
  });

  it("loads suppliers after mount", async () => {
    const { result } = renderHook(() => useSuppliersPage());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.filteredSuppliers).toBeInstanceOf(Array);
    expect(result.current.totalCount).toBeGreaterThanOrEqual(0);
  });

  it("opens create dialog", () => {
    const { result } = renderHook(() => useSuppliersPage());

    act(() => {
      result.current.openCreateDialog();
    });

    expect(result.current.formOpen).toBe(true);
    expect(result.current.formMode).toBe("create");
  });

  it("allows searching suppliers", () => {
    const { result } = renderHook(() => useSuppliersPage());

    act(() => {
      result.current.setSearch("buffet");
    });

    expect(result.current.search).toBe("buffet");
  });

  it("filters by status", () => {
    const { result } = renderHook(() => useSuppliersPage());

    act(() => {
      result.current.setStatusFilter("active");
    });

    expect(result.current.statusFilter).toBe("active");
  });
});
