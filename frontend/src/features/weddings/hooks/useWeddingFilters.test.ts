import { describe, expect, it } from "vitest";
import { renderHook } from "@/test-utils";
import { useWeddingFilters } from "@/features/weddings/hooks/useWeddingFilters";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import type { WeddingStatusFilter } from "@/features/shared/utils/weddingStatus";

const weddings: WeddingOut[] = [
  {
    uuid: "w-1",
    groom_name: "João Silva",
    bride_name: "Maria Souza",
    date: "2025-06-15",
    location: "São Paulo",
    expected_guests: 150,
    status: "IN_PROGRESS",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
  {
    uuid: "w-2",
    groom_name: "Pedro Alves",
    bride_name: "Ana Costa",
    date: "2025-07-20",
    location: "Rio de Janeiro",
    expected_guests: 200,
    status: "COMPLETED",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
  {
    uuid: "w-3",
    groom_name: "Lucas Lima",
    bride_name: "Carla Rocha",
    date: "2025-03-10",
    location: "Belo Horizonte",
    expected_guests: 80,
    status: "CANCELED",
    created_at: "2025-01-01T00:00:00Z",
    updated_at: "2025-01-01T00:00:00Z",
  },
];

function renderFilterHook(
  search: string,
  statusFilter: WeddingStatusFilter,
) {
  return renderHook(
    ({ search, statusFilter }: { search: string; statusFilter: WeddingStatusFilter }) =>
      useWeddingFilters(weddings, search, statusFilter),
    { initialProps: { search, statusFilter } },
  );
}

describe("useWeddingFilters", () => {
  it("returns all weddings when search is empty and filter is all", () => {
    const { result } = renderFilterHook("", "all");
    expect(result.current).toHaveLength(3);
  });

  it("filters by groom name", () => {
    const { result } = renderFilterHook("joão", "all");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-1");
  });

  it("filters by bride name", () => {
    const { result } = renderFilterHook("ana", "all");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-2");
  });

  it("filters by location", () => {
    const { result } = renderFilterHook("belo horizonte", "all");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-3");
  });

  it("search is case insensitive", () => {
    const { result } = renderFilterHook("MARIA", "all");
    expect(result.current).toHaveLength(1);
  });

  it("filters by status IN_PROGRESS", () => {
    const { result } = renderFilterHook("", "IN_PROGRESS");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].status).toBe("IN_PROGRESS");
  });

  it("filters by status COMPLETED", () => {
    const { result } = renderFilterHook("", "COMPLETED");
    expect(result.current).toHaveLength(1);
  });

  it("filters by status CANCELED", () => {
    const { result } = renderFilterHook("", "CANCELED");
    expect(result.current).toHaveLength(1);
  });

  it("combines search and status filter", () => {
    const { result } = renderFilterHook("lu", "CANCELED");
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-3");
  });

  it("returns empty when no match", () => {
    const { result } = renderFilterHook("ZZZ", "all");
    expect(result.current).toHaveLength(0);
  });
});
