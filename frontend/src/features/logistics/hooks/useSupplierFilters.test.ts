import { describe, expect, it } from "vitest";
import { renderHook } from "@/test-utils";
import { useSupplierFilters } from "@/features/logistics/hooks/useSupplierFilters";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { createMockSupplier } from "@/test-data";

const suppliers: SupplierOut[] = [
  createMockSupplier({ uuid: "s-1", name: "Buffet Gourmet", email: "buffet@email.com", phone: "(11) 1111-1111", cnpj: "12.345.678/0001-90", is_active: true }),
  createMockSupplier({ uuid: "s-2", name: "Fotógrafo Arte", email: "foto@email.com", phone: "(21) 2222-2222", cnpj: "98.765.432/0001-10", is_active: false }),
  createMockSupplier({ uuid: "s-3", name: "Decoração Sonho", email: "decor@email.com", phone: "(31) 3333-3333", cnpj: "11.111.111/0001-11", is_active: true }),
];

describe("useSupplierFilters", () => {
  it("returns all suppliers when search is empty and filter is all", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "", "all"),
    );
    expect(result.current).toHaveLength(3);
  });

  it("filters by name", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "buffet", "all"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].name).toBe("Buffet Gourmet");
  });

  it("filters by email", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "foto@email", "all"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("filters by phone", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "1111", "all"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("filters by cnpj", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "98.765", "all"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("search is case insensitive", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "BUFFET", "all"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("filters by active status", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "", "active"),
    );
    expect(result.current).toHaveLength(2);
    expect(result.current.every((s) => s.is_active)).toBe(true);
  });

  it("filters by inactive status", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "", "inactive"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].is_active).toBe(false);
  });

  it("combines search and status filter", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "decor", "active"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("s-3");
  });

  it("returns empty when no match", () => {
    const { result } = renderHook(() =>
      useSupplierFilters(suppliers, "ZZZ", "all"),
    );
    expect(result.current).toHaveLength(0);
  });
});
