import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";

import { ExpenseRedistributeForm } from "./ExpenseRedistributeForm";

const EXPENSE_UUID = "test-expense-uuid";

// ---------------------------------------------------------------------------
// Toast mocking – same pattern as DeleteExpenseDialog.test.tsx
// ---------------------------------------------------------------------------
const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

// ---------------------------------------------------------------------------
// Mutation hook mocking – we control isPending via a mutable object so that
// one test can render with isPending=true without affecting others.
// ---------------------------------------------------------------------------
const mockMutationState = vi.hoisted(() => ({
  isPending: false,
  mutateAsync: vi.fn<(...args: unknown[]) => Promise<unknown>>(),
}));

vi.mock(
  "@/api/generated/v1/endpoints/finances/finances",
  async (importOriginal) => {
    const actual =
      await importOriginal<
        typeof import("@/api/generated/v1/endpoints/finances/finances")
      >();
    return {
      ...actual,
      useFinancesExpensesUpdate: () => ({
        mutateAsync: mockMutationState.mutateAsync,
        isPending: mockMutationState.isPending,
      }),
    };
  },
);

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe("ExpenseRedistributeForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockMutationState.isPending = false;
  });

  it("renders with initial values from props", () => {
    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    expect(screen.getByDisplayValue("3")).toBeInTheDocument();
    expect(screen.getByDisplayValue("2025-07-15")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /aplicar/i }),
    ).toBeInTheDocument();
  });

  it("defaults first due date to today when firstExistingDate is null", () => {
    const today = new Date().toISOString().slice(0, 10);

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={1}
        firstExistingDate={null}
      />,
    );

    expect(screen.getByDisplayValue(today)).toBeInTheDocument();
    expect(screen.getByDisplayValue("1")).toBeInTheDocument();
  });

  it("changing nº de parcelas updates the input", async () => {
    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    const numInput = screen.getByDisplayValue("3");
    await user.tripleClick(numInput);
    await user.keyboard("6");

    expect(screen.getByDisplayValue("6")).toBeInTheDocument();
  });

  it("changing first due date updates the input", async () => {
    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    const dateInput = screen.getByDisplayValue("2025-07-15");
    await user.clear(dateInput);
    await user.type(dateInput, "2025-08-01");

    expect(screen.getByDisplayValue("2025-08-01")).toBeInTheDocument();
  });

  it("shows success toast on successful mutation", async () => {
    mockMutationState.mutateAsync.mockResolvedValue({});

    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    await user.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() => {
      expect(mockMutationState.mutateAsync).toHaveBeenCalledWith({
        uuid: EXPENSE_UUID,
        data: { num_installments: 3, first_due_date: "2025-07-15" },
      });
      expect(toastSuccess).toHaveBeenCalledWith(
        "Parcelas remanejadas com sucesso!",
      );
    });
  });

  it("shows error toast on failed mutation", async () => {
    mockMutationState.mutateAsync.mockRejectedValue(new Error("API Error"));

    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    await user.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() => {
      expect(toastError).toHaveBeenCalledWith(
        "Erro ao remanejar parcelas.",
      );
    });
  });

  it("button is disabled while mutation is pending", () => {
    mockMutationState.isPending = true;

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    expect(
      screen.getByRole("button", { name: /aplicar/i }),
    ).toBeDisabled();
  });
});
