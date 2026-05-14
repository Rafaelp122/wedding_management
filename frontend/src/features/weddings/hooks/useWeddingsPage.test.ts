import { describe, expect, it } from "vitest";
import { renderHook, waitFor, act } from "@/test-utils";
import { useWeddingsPage } from "@/features/weddings/hooks/useWeddingsPage";

describe("useWeddingsPage", () => {
  it("initializes with default values", () => {
    const { result } = renderHook(() => useWeddingsPage());

    expect(result.current.search).toBe("");
    expect(result.current.statusFilter).toBe("all");
    expect(result.current.createDialogOpen).toBe(false);
  });

  it("loads weddings after mount", async () => {
    const { result } = renderHook(() => useWeddingsPage());

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.filteredWeddings).toBeInstanceOf(Array);
    expect(result.current.totalCount).toBeGreaterThanOrEqual(0);
  });

  it("updates search state", () => {
    const { result } = renderHook(() => useWeddingsPage());

    act(() => {
      result.current.setSearch("joão");
    });

    expect(result.current.search).toBe("joão");
  });

  it("updates status filter", () => {
    const { result } = renderHook(() => useWeddingsPage());

    act(() => {
      result.current.setStatusFilter("COMPLETED");
    });

    expect(result.current.statusFilter).toBe("COMPLETED");
  });

  it("opens and closes create dialog", () => {
    const { result } = renderHook(() => useWeddingsPage());

    act(() => {
      result.current.setCreateDialogOpen(true);
    });

    expect(result.current.createDialogOpen).toBe(true);

    act(() => {
      result.current.setCreateDialogOpen(false);
    });

    expect(result.current.createDialogOpen).toBe(false);
  });
});
