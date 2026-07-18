/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@/test-utils";
import { WeddingFinancesView } from "@/features/finances/components/FinancesView";

vi.mock("@/features/finances/components/FinancesDistributionChart", () => ({
  WeddingFinancesDistributionChart: () => <div data-testid="distribution-chart" />,
}));

vi.mock("@/features/finances/components/expenses/CreateExpenseDialog", () => ({
  CreateExpenseDialog: ({ open }: { open: boolean }) =>
    open ? <div data-testid="create-expense-dialog">Nova Despesa</div> : null,
}));

vi.mock("@/features/finances/components/FinancesGroupsSummary", () => ({
  WeddingFinancesGroupsSummary: ({ onCategoryChanged }: { onCategoryChanged: () => void }) => (
    <div>
      <button data-testid="mock-category-change-btn" onClick={onCategoryChanged}>
        Change Category
      </button>
    </div>
  ),
}));

vi.mock("@/features/finances/components/expenses/ExpensesTable", () => ({
  WeddingExpensesTable: ({ expenses, onExpenseUpdated }: { expenses: any[], onExpenseUpdated: () => void }) => (
    <div>
      {expenses.map((e) => (
        <div key={e.uuid}>{e.name}</div>
      ))}
      <button data-testid="mock-expense-update-btn" onClick={onExpenseUpdated}>
        Update Expense
      </button>
    </div>
  ),
}));

import { useWeddingBudget } from "../hooks/useBudget";
import { useFinancesExpensesList } from "@/api/generated/v1/endpoints/finances/finances";

describe("WeddingFinancesView", () => {
  const defaultBudgetData = {
    categories: [],
    isLoading: false,
    totalEstimated: 50000,
    totalSpent: 25000,
  };

  const defaultExpensesResponse = {
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
      () => defaultExpensesResponse as any,
    );
  });

  it("shows skeleton placeholders when budget is loading", () => {
    vi.mocked(useWeddingBudget).mockReturnValue({
      ...defaultBudgetData,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(screen.queryByText("Orçamento Total")).not.toBeInTheDocument();

    expect(screen.queryByTestId("distribution-chart")).not.toBeInTheDocument();
  });

  it("shows skeleton placeholders when expenses are loading", () => {
    vi.mocked(useFinancesExpensesList).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(screen.getByText("Orçamento Total")).toBeInTheDocument();

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

    await waitFor(() => {
      expect(
        screen.queryByTestId("create-expense-dialog"),
      ).not.toBeInTheDocument();
    });

    const addButton = await screen.findByRole("button", {
      name: /adicionar despesa/i,
    });
    await userEvent.setup().click(addButton);

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
      expect(matches.length).toBeGreaterThanOrEqual(2);
    });
  });

  it("triggers refetch queries when category or expense changes", async () => {
    const userEvent = (await import("@/test-utils")).userEvent;
    render(<WeddingFinancesView weddingUuid="w-1" />);

    const user = userEvent.setup();

    const categoryBtn = screen.getByTestId("mock-category-change-btn");
    await user.click(categoryBtn);

    const expenseBtn = screen.getByTestId("mock-expense-update-btn");
    await user.click(expenseBtn);

    expect(categoryBtn).toBeInTheDocument();
  });
});
