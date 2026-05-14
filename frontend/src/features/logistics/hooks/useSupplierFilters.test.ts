import { describe, expect, it } from "vitest";
import { renderHook } from "@/test-utils";
import { useSupplierFilters } from "@/features/logistics/hooks/useSupplierFilters";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import type { SupplierStatusFilter } from "@/features/logistics/types";

const suppliers: SupplierOut[] = [
  {
    uuid: "s-1",
    name: "Buffet Gourmet",
    cnpj: "12.345.678/0001-90",
    phone: "(11) 1111-1111",
    email: "buffet@email.com",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
  {
    uuid: "s-2",
    name: "Fotógrafo Arte",
    cnpj: "98.765.432/0001-10",
    phone: "(21) 2222-2222",
    email: "foto@email.com",
    is_active: false,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
  {
    uuid: "s-3",
    name: "Decoração Sonho",
    cnpj: "11.111.111/0001-11",
    phone: "(31) 3333-3333",
    email: "decor@email.com",
    is_active: true,
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
];

function renderFilterHook(
  search: string,
  statusFilter: SupplierStatusFilter,
) {
  return renderHook(
    ({ search, statusFilter }: { search: string; statusFilter: SupplierStatusFilter }) =>
      useSupplierFilters(suppliers, search, statusFilter),
    { initialProps: { search, statusFilter } },
  );
}

describe("useSupplierFilters", () => {
  it("returns all suppliers when search is empty and filter is all", () => {
    const { result } = renderFilterHook("", "all");
    expect(result.current).toHaveLength(3);
  });

  it("filters by name", () => {
    const { result } = renderFilterHook("buffet", "all");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].name).toBe("Buffet Gourmet");
  });

  it("filters by email", () => {
    const { result } = renderFilterHook("foto@email", "all");
    expect(result.current).toHaveLength(1);
  });

  it("filters by phone", () => {
    const { result } = renderFilterHook("1111", "all");
    expect(result.current).toHaveLength(1);
  });

  it("filters by cnpj", () => {
    const { result } = renderFilterHook("98.765", "all");
    expect(result.current).toHaveLength(1);
  });

  it("search is case insensitive", () => {
    const { result } = renderFilterHook("BUFFET", "all");
    expect(result.current).toHaveLength(1);
  });

  it("filters by active status", () => {
    const { result } = renderFilterHook("", "active");
    expect(result.current).toHaveLength(2);
    expect(result.current.every((s) => s.is_active)).toBe(true);
  });

  it("filters by inactive status", () => {
    const { result } = renderFilterHook("", "inactive");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].is_active).toBe(false);
  });

  it("combines search and status filter", () => {
    const { result } = renderFilterHook("decor", "active");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("s-3");
  });

  it("returns empty when no match", () => {
    const { result } = renderFilterHook("ZZZ", "all");
    expect(result.current).toHaveLength(0);
  });
});
