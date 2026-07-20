/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
vi.unmock("@/features/finances/components/FinancesView");
import { render, screen, waitFor, server, userEvent } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingFinancesView } from "@/features/finances/components/FinancesView";
import { createMockExpense } from "@/test-data";
import type { ExpenseOut } from "@/api/generated/v1/models/expenseOut";

vi.mock("@/features/finances/components/FinancesDistributionChart", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/FinancesDistributionChart")>();
  return { ...mod, WeddingFinancesDistributionChart: () => <div data-testid="distribution-chart" /> };
});

vi.mock("@/features/finances/components/expenses/CreateExpenseDialog", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/CreateExpenseDialog")>();
  return {
    ...mod,
    CreateExpenseDialog: ({ open, onOpenChange, onSuccess }: any) =>
      open ? (
        <div data-testid="create-expense-dialog">
          Nova Despesa
          <button onClick={() => onOpenChange(false)}>Fechar criação</button>
          <button onClick={onSuccess}>Concluir criação</button>
        </div>
      ) : null,
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
    WeddingExpensesTable: ({
      expenses,
      onEditExpense,
      onDeleteExpense,
      onDetailExpense,
    }: any) => (
      <div>
        {expenses.map((e: ExpenseOut) => (
          <div key={e.uuid}>{e.name}</div>
        ))}
        {expenses[0] ? (
          <>
            <button onClick={() => onEditExpense(expenses[0])}>Editar mock</button>
            <button onClick={() => onDeleteExpense(expenses[0])}>Excluir mock</button>
            <button onClick={() => onDetailExpense(expenses[0])}>Detalhar mock</button>
          </>
        ) : null}
      </div>
    ),
  };
});

vi.mock("@/features/finances/components/expenses/EditExpenseDialog", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/EditExpenseDialog")>();
  return {
    ...mod,
    EditExpenseDialog: ({ open, onOpenChange, onSuccess }: any) =>
      open ? (
        <div data-testid="edit-expense-dialog">
          <button onClick={() => onOpenChange(false)}>Fechar edição</button>
          <button onClick={onSuccess}>Concluir edição</button>
        </div>
      ) : null,
  };
});

vi.mock("@/features/finances/components/expenses/DeleteExpenseDialog", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/DeleteExpenseDialog")>();
  return {
    ...mod,
    DeleteExpenseDialog: ({ open, onOpenChange, onSuccess }: any) =>
      open ? (
        <div data-testid="delete-expense-dialog">
          <button onClick={() => onOpenChange(false)}>Fechar exclusão</button>
          <button onClick={onSuccess}>Concluir exclusão</button>
        </div>
      ) : null,
  };
});

const mockExpense = createMockExpense({ uuid: "e-1", name: "Buffet Premium" });

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

  it("refetches budget and categories when a category changes", async () => {
    let budgetRequests = 0;
    let categoryRequests = 0;
    server.use(
      http.get("*/api/v1/finances/budgets/for-wedding/:weddingUuid/", () => {
        budgetRequests += 1;
        return HttpResponse.json({
          uuid: "b-1",
          wedding: "w-1",
          total_estimated: "50000.00",
          total_overall_spent: "25000.00",
          notes: "",
        });
      }),
      http.get("*/api/v1/finances/categories/", () => {
        categoryRequests += 1;
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    render(<WeddingFinancesView weddingUuid="w-1" />);
    const user = userEvent.setup();
    const categoryBtn = await screen.findByTestId("mock-category-change-btn");
    await user.click(categoryBtn);

    await waitFor(() => {
      expect(budgetRequests).toBeGreaterThanOrEqual(2);
      expect(categoryRequests).toBeGreaterThanOrEqual(2);
    });
  });

  it("closes creation and refreshes finance queries after success", async () => {
    let expenseRequests = 0;
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        expenseRequests += 1;
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => expect(expenseRequests).toBeGreaterThanOrEqual(2));
    const requestsBeforeSuccess = expenseRequests;

    await user.click(await screen.findByRole("button", { name: /adicionar despesa/i }));
    await user.click(screen.getByRole("button", { name: "Fechar criação" }));
    expect(screen.queryByTestId("create-expense-dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /adicionar despesa/i }));
    await user.click(screen.getByRole("button", { name: "Concluir criação" }));

    expect(screen.queryByTestId("create-expense-dialog")).not.toBeInTheDocument();
    await waitFor(() => expect(expenseRequests).toBeGreaterThan(requestsBeforeSuccess));
  });

  it("opens, closes and completes expense actions", async () => {
    let expenseRequests = 0;
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        expenseRequests += 1;
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => expect(expenseRequests).toBeGreaterThanOrEqual(2));
    const requestsBeforeActions = expenseRequests;

    await user.click(await screen.findByRole("button", { name: "Editar mock" }));
    expect(await screen.findByTestId("edit-expense-dialog")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Fechar edição" }));
    expect(screen.queryByTestId("edit-expense-dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Editar mock" }));
    await user.click(screen.getByRole("button", { name: "Concluir edição" }));
    expect(screen.queryByTestId("edit-expense-dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Excluir mock" }));
    expect(await screen.findByTestId("delete-expense-dialog")).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Fechar exclusão" }));
    expect(screen.queryByTestId("delete-expense-dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Excluir mock" }));
    await user.click(screen.getByRole("button", { name: "Concluir exclusão" }));
    expect(screen.queryByTestId("delete-expense-dialog")).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Detalhar mock" }));
    expect(screen.getByRole("button", { name: "Detalhar mock" })).toBeInTheDocument();

    await waitFor(() => expect(expenseRequests).toBeGreaterThan(requestsBeforeActions));
  });
});
