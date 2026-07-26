import { HttpResponse } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { createMockExpense } from "@/test-data";
import { useEditExpenseForm } from "./useEditExpenseForm";
import { getFinancesExpensesUpdateMockHandler } from "@/api/generated/v1/endpoints/finances/finances.msw";
import { getLogisticsContractsListMockHandler } from "@/api/generated/v1/endpoints/logistics/logistics.msw";

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
      getLogisticsContractsListMockHandler({ items: [mockContract as any], count: 1 }),
      getFinancesExpensesUpdateMockHandler(mockExpense as any),
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
      getFinancesExpensesUpdateMockHandler(async ({ request }) => {
        patchBody = await request.json();
        return { ...mockExpense, name: "Buffet Premium" } as any;
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
      getFinancesExpensesUpdateMockHandler(() => {
        throw HttpResponse.json({ detail: "Erro" }, { status: 500 });
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

  it("resets form when expense prop or open state changes", () => {
    let exp = mockExpense;
    let isOpen = true;
    const { result, rerender } = renderHook(() =>
      useEditExpenseForm({
        expense: exp,
        weddingUuid,
        open: isOpen,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.form.getValues("name")).toBe("Buffet Principal");

    exp = createMockExpense({
      ...mockExpense,
      name: "Buffet Atualizado",
    });

    rerender();

    expect(result.current.form.getValues("name")).toBe("Buffet Atualizado");

    act(() => {
      result.current.form.setValue("name", "Nome Modificado");
    });
    expect(result.current.form.getValues("name")).toBe("Nome Modificado");

    isOpen = false;
    rerender();

    isOpen = true;
    rerender();

    expect(result.current.form.getValues("name")).toBe("Buffet Atualizado");
  });

  it("triggers onOpenChange when handleOpenChange is called", () => {
    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: mockExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    act(() => {
      result.current.handleOpenChange(false);
    });

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("handles empty and null fields in expense object correctly", () => {
    const emptyExpense = createMockExpense({
      uuid: "exp-empty",
      name: "",
      description: "",
      estimated_amount: "0.00",
      actual_amount: "0.00",
      contract: null,
      paid_installments_count: undefined,
    });

    const { result } = renderHook(() =>
      useEditExpenseForm({
        expense: emptyExpense,
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.hasPaid).toBe(false);
    expect(result.current.form.getValues()).toMatchObject({
      name: "",
      description: "",
      estimated_amount: 0,
      actual_amount: 0,
      contract: null,
    });
  });
});
