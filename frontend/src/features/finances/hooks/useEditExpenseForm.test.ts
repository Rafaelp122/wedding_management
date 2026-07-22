import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { createMockExpense } from "@/test-data";
import { useEditExpenseForm } from "./useEditExpenseForm";

describe("useEditExpenseForm", () => {
  const weddingUuid = "wedding-1";
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();
  const mockExpense = createMockExpense({
    uuid: "exp-123",
    name: "Buffet Principal",
    estimated_amount: "5000.00",
    actual_amount: "4800.00",
    paid_installments_count: 0,
  });

  const mockContract = {
    uuid: "contract-1",
    description: "Contrato Buffet",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [mockContract], count: 1 });
      }),
      http.patch("*/api/v1/finances/expenses/:uuid/", () => {
        return HttpResponse.json({ ...mockExpense }, { status: 200 });
      }),
    );
  });

  it("initializes form with pre-filled expense values and hasPaid as false", async () => {
    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: mockExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.hasPaid).toBe(false);
    expect(result.current.form.getValues()).toMatchObject({
      name: "Buffet Principal",
      description: mockExpense.description || "",
      estimated_amount: 5000,
      actual_amount: 4800,
      contract: mockExpense.contract || null,
      num_installments: null,
      first_due_date: null,
    });

    await waitFor(() => {
      expect(result.current.contracts).toHaveLength(1);
    });
  });

  it("identifies hasPaid as true when paid_installments_count > 0", () => {
    const paidExpense = createMockExpense({
      ...mockExpense,
      paid_installments_count: 2,
    });

    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: paidExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.hasPaid).toBe(true);
  });

  it("submits patch payload containing only modified fields", async () => {
    let patchBody: unknown;
    server.use(
      http.patch("*/api/v1/finances/expenses/:uuid/", async ({ request }) => {
        patchBody = await request.json();
        return HttpResponse.json({ ...mockExpense, name: "Buffet Premium" });
      }),
    );

    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: mockExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    const modifiedData = {
      ...result.current.form.getValues(),
      name: "Buffet Premium",
    };

    act(() => {
      result.current.onSubmit(modifiedData);
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Despesa atualizada com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });

    expect(patchBody).toEqual({
      name: "Buffet Premium",
    });
  });

  it("handles errors when expense update fails", async () => {
    server.use(
      http.patch("*/api/v1/finances/expenses/:uuid/", () => {
        return HttpResponse.json({ detail: "Erro" }, { status: 500 });
      }),
    );

    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: mockExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    act(() => {
      result.current.onSubmit({
        ...result.current.form.getValues(),
        name: "Nome Alterado",
      });
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro");
    });
  });
});
