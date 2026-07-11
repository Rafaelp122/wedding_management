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
    vi.mocked(useFinancesExpensesList).mockImplementation(
      () => {
        return defaultExpensesData as any;
      },
    );
  });

  it("shows skeleton placeholders when budget is loading", () => {
    vi.mocked(useWeddingBudget).mockReturnValue({
      ...defaultBudgetData,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    // Os cards de resumo não devem aparecer — skeletons os substituem
    expect(screen.queryByText("Orçamento Total")).not.toBeInTheDocument();
    // O gráfico e as categorias também são substituídos por skeletons
    expect(screen.queryByTestId("distribution-chart")).not.toBeInTheDocument();
  });

  it("shows skeleton placeholders when expenses are loading", () => {
    vi.mocked(useFinancesExpensesList).mockReturnValue({
      ...defaultExpensesData,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    // As seções de orçamento (não loading) devem aparecer normalmente
    expect(screen.getByText("Orçamento Total")).toBeInTheDocument();
    // Despesas recentes e tabela não devem aparecer — skeletons os substituem
    expect(screen.queryByText("Despesas Recentes")).not.toBeInTheDocument();
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

    const fullExpensesData = {
      data: {
        data: {
          items: [mockExpense],
          count: 1,
        },
      },
      isLoading: false,
    };

    const recentExpensesData = {
      data: {
        data: {
          items: [mockExpense],
          count: 1,
        },
      },
      isLoading: false,
    };

    vi.mocked(useFinancesExpensesList).mockImplementation(
      (params?: { wedding_id?: string | null; limit?: number; offset?: number }) => {
        if (params?.limit === 5) {
          return recentExpensesData as any;
        }
        return fullExpensesData as any;
      },
    );

    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => {
      const matches = screen.getAllByText("Buffet Premium");
      // Appears in both RecentExpenses card and ExpensesTable rows
      expect(matches.length).toBeGreaterThanOrEqual(2);
    });

    expect(useFinancesExpensesList).toHaveBeenCalledWith(
      expect.objectContaining({ wedding_id: "w-1", limit: 5 }),
    );
  });
});
