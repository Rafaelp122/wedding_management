import { describe, expect, it, vi, beforeAll } from "vitest";
import { renderHook, waitFor, act } from "@/test-utils";
import type { useWeddingBudget as UseWeddingBudgetType } from "@/features/finances/hooks/useBudget";

let useWeddingBudget: typeof UseWeddingBudgetType;

beforeAll(async () => {
  const mod = await vi.importActual<typeof import("@/features/finances/hooks/useBudget")>(
    "@/features/finances/hooks/useBudget",
  );
  useWeddingBudget = mod.useWeddingBudget;
});

describe("useWeddingBudget", () => {
  const weddingUuid = "test-wedding-uuid";

  it("returns budget data after loading", async () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.budgetError).toBeNull();
  });

  it("starts in non-editing mode", async () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    expect(result.current.isEditing).toBe(false);
  });

  it("enters edit mode on handleEditInit", async () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.handleEditInit();
    });

    expect(result.current.isEditing).toBe(true);
  });

  it("cancels edit on handleCancelEdit", async () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
    });

    act(() => {
      result.current.handleEditInit();
    });

    act(() => {
      result.current.handleCancelEdit();
    });

    expect(result.current.isEditing).toBe(false);
  });

  it("calculates progress percentage", () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    expect(typeof result.current.progressPercentage).toBe("number");
    expect(result.current.progressPercentage).toBeGreaterThanOrEqual(0);
  });

  it("sets a progress color", () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    expect(result.current.progressColor).toMatch(/^bg-(red|yellow|green)-500$/);
  });
});
