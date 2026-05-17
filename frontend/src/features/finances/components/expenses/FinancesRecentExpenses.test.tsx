import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, within } from "@/test-utils";
import { WeddingFinancesRecentExpenses } from "./FinancesRecentExpenses";
import { createMockExpense } from "@/test-data";

// ---------------------------------------------------------------------------
// Mock the lazy-loaded ExpenseDetailDialog so it renders synchronously.
// Because vi.mock is hoisted, the dynamic import inside React.lazy resolves
// to this component immediately under test.
// ---------------------------------------------------------------------------
vi.mock("./ExpenseDetailDialog", () => ({
  ExpenseDetailDialog: ({
    expense,
    open,
    onOpenChange,
  }: {
    expense: { name: string };
    open: boolean;
    onOpenChange: (open: boolean) => void;
  }) =>
    open ? (
      <div data-testid="expense-detail-dialog">
        <span>{expense.name}</span>
        <button onClick={() => onOpenChange(false)}>close</button>
      </div>
    ) : null,
}));

describe("WeddingFinancesRecentExpenses", () => {
  // -----------------------------------------------------------------------
  // 1. Renders expense cards with correct info
  // -----------------------------------------------------------------------
  it("renders expense cards with name, category, amount, status", () => {
    const expenses = [
      createMockExpense({
        uuid: "e-1",
        name: "Buffet Principal",
        category_name: "Buffet",
        actual_amount: "4800.00",
        status: "PARTIALLY_PAID",
        installments_count: 3,
        paid_installments_count: 1,
      }),
      createMockExpense({
        uuid: "e-2",
        name: "Decoração Luxo",
        category_name: "Decoração",
        actual_amount: "2500.00",
        status: "SETTLED",
        installments_count: 0,
        paid_installments_count: 0,
      }),
    ];

    render(<WeddingFinancesRecentExpenses expenses={expenses} />);

    // Card title
    expect(screen.getByText("Despesas Recentes")).toBeInTheDocument();

    // Expense names
    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
    expect(screen.getByText("Decoração Luxo")).toBeInTheDocument();

    // Category names
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("Decoração")).toBeInTheDocument();

    // Formatted amounts (R$ non-breaking-space value)
    expect(screen.getByText(/R\$\s*4\.800/)).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*2\.500/)).toBeInTheDocument();

    // Status badges
    expect(screen.getByText("Parcial")).toBeInTheDocument();
    expect(screen.getByText("Quitada")).toBeInTheDocument();

    // Installment count
    expect(screen.getByText("1/3 parcelas")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 2. Shows empty state when no expenses
  // -----------------------------------------------------------------------
  it("shows empty state when expenses is empty", () => {
    render(<WeddingFinancesRecentExpenses expenses={[]} />);

    expect(
      screen.getByText("Nenhuma despesa registrada no sistema."),
    ).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 3. Calls onAddExpense when "Adicionar Despesa" button is clicked
  // -----------------------------------------------------------------------
  it("calls onAddExpense when Adicionar Despesa button is clicked", async () => {
    const onAddExpense = vi.fn();
    const user = userEvent.setup();

    render(
      <WeddingFinancesRecentExpenses
        expenses={[createMockExpense()]}
        onAddExpense={onAddExpense}
      />,
    );

    await user.click(
      screen.getByRole("button", { name: /adicionar despesa/i }),
    );

    expect(onAddExpense).toHaveBeenCalledTimes(1);
  });

  // -----------------------------------------------------------------------
  // 4. Opens detail dialog when an expense card is clicked
  // -----------------------------------------------------------------------
  it("opens detail dialog when an expense card is clicked", async () => {
    const user = userEvent.setup();
    const expense = createMockExpense({ uuid: "e-1", name: "Buffet Premium" });

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    // Click on the expense name
    await user.click(screen.getByText("Buffet Premium"));

    // The mocked dialog should appear (use findBy because React.lazy
    // requires an extra render cycle even with the mock in place)
    const dialog = await screen.findByTestId("expense-detail-dialog");
    expect(dialog).toBeInTheDocument();

    // Expense name is shown inside the dialog
    expect(within(dialog).getByText("Buffet Premium")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 5. Closes dialog when onOpenChange is called with false
  // -----------------------------------------------------------------------
  it("closes dialog when close button is clicked", async () => {
    const user = userEvent.setup();
    const expense = createMockExpense({ uuid: "e-1", name: "Buffet Premium" });

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    // Open the dialog
    await user.click(screen.getByText("Buffet Premium"));
    const dialog = await screen.findByTestId("expense-detail-dialog");
    expect(dialog).toBeInTheDocument();

    // Close by clicking the "close" button rendered inside the mock
    await user.click(within(dialog).getByRole("button", { name: /close/i }));

    expect(
      screen.queryByTestId("expense-detail-dialog"),
    ).not.toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 6. Renders a fallback when name/description is missing
  // -----------------------------------------------------------------------
  it('renders "N/A" fallback when name and description are empty', () => {
    const expense = createMockExpense({
      name: undefined,
      description: undefined,
    });

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
