import { describe, expect, it, vi, beforeAll, beforeEach } from "vitest";
import { renderHook, waitFor, act, server } from "@/test-utils";
import type { useWeddingBudget as UseWeddingBudgetType } from "@/features/finances/hooks/useBudget";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";

let useWeddingBudget: typeof UseWeddingBudgetType;

beforeAll(async () => {
  const mod = await vi.importActual<typeof import("@/features/finances/hooks/useBudget")>(
    "@/features/finances/hooks/useBudget",
  );
  useWeddingBudget = mod.useWeddingBudget;
});

describe("useWeddingBudget", () => {
  const weddingUuid = "test-wedding-uuid";

  beforeEach(() => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({
          uuid: "budget-1",
          wedding: weddingUuid,
          total_estimated: "1000.00",
          total_overall_spent: "500.00",
          notes: "",
        }),
      ),
      http.get("*/api/v1/finances/categories/", () =>
        HttpResponse.json({
          items: [
            { uuid: "c-1", allocated_budget: "300.00" },
            { uuid: "c-2", allocated_budget: null },
          ],
          count: 2,
        }),
      ),
    );
  });

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

  it("calculates totals and green progress", async () => {
    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    await waitFor(() => expect(result.current.isLoading).toBe(false));

    expect(result.current.totalEstimated).toBe(1000);
    expect(result.current.totalSpent).toBe(500);
    expect(result.current.totalAllocated).toBe(300);
    expect(result.current.progressPercentage).toBe(50);
    expect(result.current.progressColor).toBe("bg-green-500");
  });

  it.each([
    ["900.00", "bg-yellow-500"],
    ["1100.00", "bg-red-500"],
  ])("uses the expected color for %s spent", async (spent, color) => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({
          uuid: "budget-1",
          wedding: weddingUuid,
          total_estimated: "1000.00",
          total_overall_spent: spent,
        }),
      ),
    );

    const { result } = renderHook(() => useWeddingBudget(weddingUuid));

    await waitFor(() => expect(result.current.isLoading).toBe(false));
    expect(result.current.progressColor).toBe(color);
  });

  it("does not enter edit mode or save without a budget", async () => {
    let updateRequests = 0;
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({ detail: "Not found" }, { status: 404 }),
      ),
      http.patch("*/api/v1/finances/budgets/:uuid/", () => {
        updateRequests += 1;
        return HttpResponse.json({});
      }),
    );

    const { result } = renderHook(() => useWeddingBudget(weddingUuid));
    await waitFor(() => expect(result.current.budgetError).toBeTruthy());

    act(() => result.current.handleEditInit());
    await act(async () => result.current.handleSave());

    expect(result.current.isEditing).toBe(false);
    expect(updateRequests).toBe(0);
  });

  it("updates the budget and refreshes related queries", async () => {
    let budgetRequests = 0;
    let categoryRequests = 0;
    let requestBody: unknown;
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () => {
        budgetRequests += 1;
        return HttpResponse.json({
          uuid: "budget-1",
          wedding: weddingUuid,
          total_estimated: "1000.00",
          total_overall_spent: "500.00",
        });
      }),
      http.get("*/api/v1/finances/categories/", () => {
        categoryRequests += 1;
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.patch("*/api/v1/finances/budgets/:uuid/", async ({ request }) => {
        requestBody = await request.json();
        return HttpResponse.json({
          uuid: "budget-1",
          wedding: weddingUuid,
          total_estimated: "1500.00",
          total_overall_spent: "500.00",
        });
      }),
    );

    const { result } = renderHook(() => useWeddingBudget(weddingUuid));
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => {
      result.current.handleEditInit();
      result.current.setEditTotal("1500.00");
    });
    await act(async () => result.current.handleSave());

    expect(requestBody).toEqual({ total_estimated: "1500.00" });
    expect(toast.success).toHaveBeenCalledWith("Orçamento atualizado com sucesso!");
    expect(result.current.isEditing).toBe(false);
    await waitFor(() => {
      expect(budgetRequests).toBeGreaterThanOrEqual(2);
      expect(categoryRequests).toBeGreaterThanOrEqual(2);
    });
  });

  it("keeps edit mode open when the update fails", async () => {
    server.use(
      http.patch("*/api/v1/finances/budgets/:uuid/", () =>
        HttpResponse.json({ detail: "Falha de validação" }, { status: 400 }),
      ),
    );

    const { result } = renderHook(() => useWeddingBudget(weddingUuid));
    await waitFor(() => expect(result.current.isLoading).toBe(false));

    act(() => result.current.handleEditInit());
    await act(async () => result.current.handleSave());

    expect(toast.error).toHaveBeenCalled();
    expect(result.current.isEditing).toBe(true);
  });
});
