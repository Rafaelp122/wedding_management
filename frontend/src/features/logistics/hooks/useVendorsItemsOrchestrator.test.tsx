import React from "react";
import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
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

    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );

    const { result } = renderHook(() => useVendorsItemsOrchestrator(), { wrapper });

    act(() => {
      result.current.refreshItems();
    });

    expect(spy).toHaveBeenCalled();
  });
});
