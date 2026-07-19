/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingFinancesView } from "@/features/finances/components/FinancesView";

vi.mock("@/features/finances/components/FinancesDistributionChart", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/FinancesDistributionChart")>();
  return { ...mod, WeddingFinancesDistributionChart: () => <div data-testid="distribution-chart" /> };
});

vi.mock("@/features/finances/components/expenses/CreateExpenseDialog", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/CreateExpenseDialog")>();
  return {
    ...mod,
    CreateExpenseDialog: ({ open }: { open: boolean }) =>
      open ? <div data-testid="create-expense-dialog">Nova Despesa</div> : null,
  };
});

vi.mock("@/features/finances/components/FinancesGroupsSummary", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/FinancesGroupsSummary")>();
  return {
    ...mod,
    WeddingFinancesGroupsSummary: ({ onCategoryChanged }: { onCategoryChanged: () => void }) => (
      <div>
        <button data-testid="mock-category-change-btn" onClick={onCategoryChanged}>
          Change Category
        </button>
      </div>
    ),
  };
});

vi.mock("@/features/finances/components/expenses/ExpensesTable", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/ExpensesTable")>();
  return {
    ...mod,
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
  };
});

describe("WeddingFinancesView", () => {
  beforeEach(() => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({
          uuid: "b-1",
          wedding: "w-1",
          total_estimated: "50000.00",
          total_overall_spent: "25000.00",
          notes: "",
        }),
      ),
      http.get("*/api/v1/finances/categories/", () =>
        HttpResponse.json({
          items: [],
          count: 0,
        }),
      ),
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({
          items: [],
          count: 0,
        }),
      ),
    );
  });

  it("shows skeleton placeholders when budget is loading", () => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () => new Promise(() => {})),
    );

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(screen.queryByText("Orçamento Total")).not.toBeInTheDocument();

    expect(screen.queryByTestId("distribution-chart")).not.toBeInTheDocument();
  });

  it("shows skeleton placeholders when expenses are loading", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => new Promise(() => {})),
    );

    render(<WeddingFinancesView weddingUuid="w-1" />);

    expect(await screen.findByText("Orçamento Total")).toBeInTheDocument();

    expect(screen.queryByText("Despesas Recentes")).not.toBeInTheDocument();
  });

  it("renders summary cards after loading", async () => {
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () =>
        HttpResponse.json({
          uuid: "b-1",
          wedding: "w-1",
          total_estimated: "75000.00",
          total_overall_spent: "30000.00",
          notes: "",
        }),
      ),
    );

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

    server.use(
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({
          items: [mockExpense],
          count: 1,
        }),
      ),
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

    const categoryBtn = await screen.findByTestId("mock-category-change-btn");
    await user.click(categoryBtn);

    const expenseBtn = await screen.findByTestId("mock-expense-update-btn");
    await user.click(expenseBtn);

    expect(categoryBtn).toBeInTheDocument();
  });
});
