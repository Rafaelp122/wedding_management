import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { QueryClient } from "@tanstack/react-query";
import { useVendorsItemsOrchestrator } from "./useVendorsItemsOrchestrator";

describe("useVendorsItemsOrchestrator", () => {
  it("initializes with default state values", () => {
    const { result } = renderHook(() => useVendorsItemsOrchestrator());

    expect(result.current.detailContractUuid).toBeNull();
    expect(result.current.uploadOpen).toBe(false);
    expect(result.current.prefilledParentUuid).toBeNull();
    expect(result.current.createItemOpen).toBe(false);
    expect(result.current.editItem).toBeNull();
  });

  it("handles new contract click", () => {
    const { result } = renderHook(() => useVendorsItemsOrchestrator());

    act(() => {
      result.current.handleNewContractClick();
    });

    expect(result.current.prefilledParentUuid).toBeNull();
    expect(result.current.uploadOpen).toBe(true);
  });

  it("handles creating addendum click", () => {
    const { result } = renderHook(() => useVendorsItemsOrchestrator());

    act(() => {
      result.current.handleCreateAddendum("parent-uuid-123");
    });

    expect(result.current.prefilledParentUuid).toBe("parent-uuid-123");
    expect(result.current.uploadOpen).toBe(true);
    expect(result.current.detailContractUuid).toBeNull();
  });

  it("invalidates queries on refreshItems call", () => {
    const queryClient = new QueryClient();
    const spy = vi.spyOn(queryClient, "invalidateQueries");

    const { result } = renderHook(() => useVendorsItemsOrchestrator(), {
      queryClient,
    });

    act(() => {
      result.current.refreshItems();
    });

    expect(spy).toHaveBeenCalled();
  });

  it("handles state setters correctly", () => {
    const mockItem = { uuid: "item-1", name: "Som e Iluminação" } as any;
    const { result } = renderHook(() => useVendorsItemsOrchestrator());

    act(() => {
      result.current.setDetailContractUuid("contract-2");
      result.current.setUploadOpen(true);
      result.current.setCreateItemOpen(true);
      result.current.setEditItem(mockItem);
    });

    expect(result.current.detailContractUuid).toBe("contract-2");
    expect(result.current.uploadOpen).toBe(true);
    expect(result.current.createItemOpen).toBe(true);
    expect(result.current.editItem).toBe(mockItem);
  });
});
