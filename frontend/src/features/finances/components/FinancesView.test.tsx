/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingFinancesView } from "@/features/finances/components/FinancesView";

// Mock lazy sub-components to avoid suspense boundaries and import issues
vi.mock("@/features/finances/components/FinancesDistributionChart", () => ({
  WeddingFinancesDistributionChart: () => <div data-testid="distribution-chart" />,
}));

vi.mock("@/features/finances/components/expenses/CreateExpenseDialog", () => ({
  CreateExpenseDialog: ({ open }: { open: boolean }) =>
    open ? <div data-testid="create-expense-dialog">Nova Despesa</div> : null,
}));

// Mock the useWeddingBudget hook
vi.mock("@/features/finances/hooks/useBudget", () => ({
  useWeddingBudget: vi.fn(),
}));

// Mock useFinancesExpensesList only, keep all other exports original
vi.mock("@/api/generated/v1/endpoints/finances/finances", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/api/generated/v1/endpoints/finances/finances")>();
  return {
    ...mod,
    useFinancesExpensesList: vi.fn(),
  };
});

import { useWeddingBudget } from "@/features/finances/hooks/useBudget";
import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";

describe("WeddingFinancesView", () => {
  const defaultBudgetData = {
    categories: [],
    isLoading: false,
    totalEstimated: 50000,
    totalSpent: 25000,
  };

  const defaultExpensesData = {
    data: {
      data: {
        items: [],
        count: 0,
      },
    },
    isLoading: false,
  };

  beforeEach(() => {
    vi.mocked(useWeddingBudget).mockReturnValue(defaultBudgetData as any);
    vi.mocked(useFinancesExpensesList).mockReturnValue(
      defaultExpensesData as any,
    );
  });

  it("shows loading state when budget is loading", () => {
    vi.mocked(useWeddingBudget).mockReturnValue({
      ...defaultBudgetData,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(
      screen.getByText("Carregando dados financeiros..."),
    ).toBeInTheDocument();
    expect(screen.getByText(/carregando dados financeiros/i)).toHaveClass(
      "animate-pulse",
    );
  });

  it("shows loading state when expenses are loading", () => {
    vi.mocked(useFinancesExpensesList).mockReturnValue({
      ...defaultExpensesData,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(
      screen.getByText("Carregando dados financeiros..."),
    ).toBeInTheDocument();
  });

  it("renders summary cards after loading", async () => {
    vi.mocked(useWeddingBudget).mockReturnValue({
      categories: [],
      isLoading: false,
      totalEstimated: 75000,
      totalSpent: 30000,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => {
      expect(screen.getByText("Orçamento Total")).toBeInTheDocument();
      expect(screen.getByText("Total Gasto")).toBeInTheDocument();
      expect(screen.getByText("Saldo Disponível")).toBeInTheDocument();
    });
  });

  it("renders recent expenses section and add expense button", async () => {
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => {
      expect(screen.getByText("Despesas Recentes")).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /adicionar despesa/i }),
      ).toBeInTheDocument();
    });
  });

  it("renders the distribution chart placeholder", async () => {
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByTestId("distribution-chart"),
      ).toBeInTheDocument();
    });
  });

  it("opens the create expense dialog when add button is clicked", async () => {
    const userEvent = (await import("@/test-utils")).userEvent;
    render(<WeddingFinancesView weddingUuid="w-1" />);

    // Dialog should not be visible initially
    await waitFor(() => {
      expect(
        screen.queryByTestId("create-expense-dialog"),
      ).not.toBeInTheDocument();
    });

    // Click the add expense button
    const addButton = await screen.findByRole("button", {
      name: /adicionar despesa/i,
    });
    await userEvent.setup().click(addButton);

    // Dialog should now be visible
    await waitFor(() => {
      expect(
        screen.getByTestId("create-expense-dialog"),
      ).toBeInTheDocument();
    });
  });

  it("renders expense table when there are expenses", async () => {
    const mockExpense = {
      uuid: "e-1",
      wedding: "w-1",
      category: "c-1",
      name: "Buffet Premium",
      estimated_amount: "5000.00",
      actual_amount: "4800.00",
      category_name: "Alimentação",
      installments_count: 3,
      paid_installments_count: 1,
      status: "PARTIALLY_PAID",
    };

    vi.mocked(useFinancesExpensesList).mockReturnValue({
      data: {
        data: {
          items: [mockExpense],
          count: 1,
        },
      },
      isLoading: false,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => {
      const matches = screen.getAllByText("Buffet Premium");
      // Appears in both RecentExpenses card and ExpensesTable rows
      expect(matches.length).toBeGreaterThanOrEqual(2);
    });
  });
});
