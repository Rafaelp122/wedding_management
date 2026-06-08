import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ExpenseDetailSheet } from "./ExpenseDetailSheet";
import { createMockExpense } from "@/test-data";

// ---------------------------------------------------------------------------
// Mock sub-components so we don't need to worry about their internals
// ---------------------------------------------------------------------------
vi.mock("./ExpenseInstallmentRow", () => ({
  ExpenseInstallmentRow: ({ installment }: { installment: { installment_number: number } }) => (
    <tr data-testid="expense-installment-row">
      <td>{installment.installment_number}</td>
    </tr>
  ),
}));

vi.mock("./ExpenseRedistributeForm", () => ({
  ExpenseRedistributeForm: () => (
    <div data-testid="expense-redistribute-form" />
  ),
}));

// ---------------------------------------------------------------------------
// Hoisted mocks for the Orval-generated hooks – we make them functions so
// each test can control exactly what each hook returns.
// ---------------------------------------------------------------------------
const mockExpensesRead = vi.hoisted(() => vi.fn());
const mockInstallmentsList = vi.hoisted(() => vi.fn());

vi.mock(
  "@/api/generated/v1/endpoints/finances/finances",
  async (importOriginal) => {
    const actual =
      await importOriginal<
        typeof import("@/api/generated/v1/endpoints/finances/finances")
      >();
    return {
      ...actual,
      useFinancesExpensesRead: (uuid: string) => mockExpensesRead(uuid),
      useFinancesInstallmentsList: (params: unknown) =>
        mockInstallmentsList(params),
      useFinancesInstallmentsMarkAsPaid: () => ({ mutateAsync: vi.fn() }),
      useFinancesInstallmentsUnmarkAsPaid: () => ({ mutateAsync: vi.fn() }),
    };
  },
);

describe("ExpenseDetailSheet", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default mocks: expense with all standard fields, empty installments
    mockExpensesRead.mockReturnValue({
      data: { data: createMockExpense() },
    });
    mockInstallmentsList.mockReturnValue({
      data: { data: { items: [], count: 0 } },
      isLoading: false,
    });
  });

  // -----------------------------------------------------------------------
  // 1. Renders expense name in the sheet title
  // -----------------------------------------------------------------------
  it("renders expense name in the sheet title", () => {
    const expense = createMockExpense({ name: "Buffet Principal" });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 2. Shows category name
  // -----------------------------------------------------------------------
  it("shows category name", () => {
    const expense = createMockExpense({ category_name: "Buffet" });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // The category name appears inside a <span> after "Categoria:"
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText(/categoria:/i)).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 3. Shows contract description when present
  // -----------------------------------------------------------------------
  it("shows contract description when present", () => {
    const expense = createMockExpense({
      contract_description: "Buffet Contrato 2025",
    });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText(/contrato:/i)).toBeInTheDocument();
    expect(screen.getByText("Buffet Contrato 2025")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 4. Shows status badge
  // -----------------------------------------------------------------------
  it("shows status badge", () => {
    const expense = createMockExpense({ status: "PARTIALLY_PAID" });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // constant.tsx maps PARTIALLY_PAID → "Parcial"
    expect(screen.getByText("Parcial")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 5. Shows progress bar with paid/total counts
  // -----------------------------------------------------------------------
  it("shows progress bar with paid/total counts", () => {
    const expense = createMockExpense({
      paid_installments_count: 1,
      installments_count: 3,
      total_paid: "1500.00",
      actual_amount: "4800.00",
    });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // The text "1/3 marcadas como pagas"
    expect(screen.getByText(/1\/3 marcadas como pagas/i)).toBeInTheDocument();

    // A Radix progressbar is rendered
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 6. Shows "Remanejar" button when no installments are paid (paidCount=0)
  //     and clicking it toggles ExpenseRedistributeForm
  // -----------------------------------------------------------------------
  it('shows "Remanejar" button when no installments are paid and toggles redistribute form', async () => {
    const expense = createMockExpense({ paid_installments_count: 0 });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // Button is visible
    const remanejarBtn = screen.getByRole("button", { name: /remanejar/i });
    expect(remanejarBtn).toBeInTheDocument();

    // Form not visible initially
    expect(
      screen.queryByTestId("expense-redistribute-form"),
    ).not.toBeInTheDocument();

    // Click once – form appears
    await user.click(remanejarBtn);
    expect(
      screen.getByTestId("expense-redistribute-form"),
    ).toBeInTheDocument();

    // Click again – form disappears
    await user.click(screen.getByRole("button", { name: /remanejar/i }));
    expect(
      screen.queryByTestId("expense-redistribute-form"),
    ).not.toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 7. Hides "Remanejar" when installments are paid (paidCount>0)
  // -----------------------------------------------------------------------
  it('hides "Remanejar" when installments are paid', () => {
    const expense = createMockExpense({ paid_installments_count: 1 });
    mockExpensesRead.mockReturnValue({ data: { data: expense } });

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(
      screen.queryByRole("button", { name: /remanejar/i }),
    ).not.toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 8. Shows loading skeleton when installments are loading
  // -----------------------------------------------------------------------
  it("shows loading skeleton when installments are loading", () => {
    mockInstallmentsList.mockReturnValue({
      data: undefined,
      isLoading: true,
    });

    render(
      <ExpenseDetailSheet
        expense={createMockExpense()}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    // The skeleton is rendered inside a Radix portal, so we search document.body
    expect(
      document.body.querySelector(".animate-pulse"),
    ).toBeInTheDocument();

    // Empty state text should NOT appear while loading
    expect(
      screen.queryByText("Nenhuma parcela encontrada."),
    ).not.toBeInTheDocument();

    // Installment rows should NOT appear while loading
    expect(
      screen.queryByTestId("expense-installment-row"),
    ).not.toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 9. Shows "Nenhuma parcela encontrada" when installments are empty
  // -----------------------------------------------------------------------
  it('shows "Nenhuma parcela encontrada" when installments are empty', () => {
    // Default mock already returns empty items; be explicit for clarity
    mockInstallmentsList.mockReturnValue({
      data: { data: { items: [], count: 0 } },
      isLoading: false,
    });

    render(
      <ExpenseDetailSheet
        expense={createMockExpense()}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Nenhuma parcela encontrada."),
    ).toBeInTheDocument();
  });
});
