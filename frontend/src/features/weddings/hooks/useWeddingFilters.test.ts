import { describe, expect, it } from "vitest";
import { renderHook } from "@/test-utils";
import { useWeddingFilters } from "@/features/weddings/hooks/useWeddingFilters";
import type { WeddingOut } from "@/api/generated/v1/models/weddingOut";
import { createMockWedding } from "@/test-data";

const weddings: WeddingOut[] = [
  createMockWedding({ uuid: "w-1", groom_name: "João Silva", bride_name: "Maria Souza", location: "São Paulo", expected_guests: 150, status: "IN_PROGRESS" }),
  createMockWedding({ uuid: "w-2", groom_name: "Pedro Alves", bride_name: "Ana Costa", location: "Rio de Janeiro", expected_guests: 200, status: "COMPLETED" }),
  createMockWedding({ uuid: "w-3", groom_name: "Lucas Lima", bride_name: "Carla Rocha", location: "Belo Horizonte", expected_guests: 80, status: "CANCELED" }),
];

describe("useWeddingFilters", () => {
  it("returns all weddings when search is empty and filter is all", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "", "all"),
    );
    expect(result.current).toHaveLength(3);
  });

  it("filters by groom name", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "joão", "all"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-1");
  });

  it("filters by bride name", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "ana", "all"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-2");
  });

  it("filters by location", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "belo horizonte", "all"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-3");
  });

  it("search is case insensitive", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "MARIA", "all"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("filters by status IN_PROGRESS", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "", "IN_PROGRESS"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].status).toBe("IN_PROGRESS");
  });

  it("filters by status COMPLETED", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "", "COMPLETED"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("filters by status CANCELED", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "", "CANCELED"),
    );
    expect(result.current).toHaveLength(1);
  });

  it("combines search and status filter", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "lu", "CANCELED"),
    );
    expect(result.current).toHaveLength(1);
    expect(result.current[0].uuid).toBe("w-3");
  });

  it("returns empty when no match", () => {
    const { result } = renderHook(() =>
      useWeddingFilters(weddings, "ZZZ", "all"),
    );
    expect(result.current).toHaveLength(0);
  });
});
