import type { ComponentProps } from "react";
import { describe, expect, it, vi, beforeEach } from "vitest";
vi.unmock("@/features/finances/components/FinancesView");
import { render, screen, waitFor, server, userEvent } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingFinancesView } from "@/features/finances/components/FinancesView";
import { createMockExpense } from "@/test-data";
import "@/features/finances/components/expenses/ExpenseDetailSheet";

vi.mock("@/features/finances/components/FinancesDistributionChart", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/FinancesDistributionChart")>();
  return { ...mod, WeddingFinancesDistributionChart: () => <div data-testid="distribution-chart" /> };
});

vi.mock("@/features/finances/components/expenses/CreateExpenseDialog", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/features/finances/components/expenses/CreateExpenseDialog")>();
  return {
    ...mod,
    CreateExpenseDialog: ({
      open,
      onOpenChange,
      onSuccess,
    }: ComponentProps<typeof mod.CreateExpenseDialog>) =>
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
    }: ComponentProps<typeof mod.WeddingExpensesTable>) => (
      <div>
        {expenses.map((e) => (
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

  it("opens, closes and updates an expense", async () => {
    let expenseRequests = 0;
    let updateRequests = 0;
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        expenseRequests += 1;
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.patch("*/api/v1/finances/expenses/:uuid/", () => {
        updateRequests += 1;
        return HttpResponse.json(mockExpense);
      }),
    );

    const user = userEvent.setup();
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => expect(expenseRequests).toBeGreaterThanOrEqual(2));
    const requestsBeforeActions = expenseRequests;

    await user.click(await screen.findByRole("button", { name: "Editar mock" }));
    expect(
      await screen.findByRole("heading", { name: "Editar Despesa" }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Editar Despesa" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Editar mock" }));
    await user.click(screen.getByRole("button", { name: "Salvar Alterações" }));
    await waitFor(() => {
      expect(updateRequests).toBeGreaterThanOrEqual(1);
      expect(
        screen.queryByRole("heading", { name: "Editar Despesa" }),
      ).not.toBeInTheDocument();
    });

    await waitFor(() =>
      expect(expenseRequests).toBeGreaterThan(requestsBeforeActions),
    );
  });

  it("opens, closes and deletes an expense", async () => {
    let expenseRequests = 0;
    let deleteRequests = 0;
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        expenseRequests += 1;
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.delete("*/api/v1/finances/expenses/:uuid/", () => {
        deleteRequests += 1;
        return new HttpResponse(null, { status: 204 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await waitFor(() => expect(expenseRequests).toBeGreaterThanOrEqual(2));
    const requestsBeforeDelete = expenseRequests;

    await user.click(await screen.findByRole("button", { name: "Excluir mock" }));
    expect(
      await screen.findByRole("heading", { name: "Deletar Despesa" }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Deletar Despesa" })).not.toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Excluir mock" }));
    await user.type(
      screen.getByPlaceholderText(/digite o nome aqui/i),
      "Buffet Premium",
    );
    await user.click(
      screen.getByRole("button", { name: "Deletar Permanentemente" }),
    );
    await waitFor(() => {
      expect(deleteRequests).toBe(1);
      expect(screen.queryByRole("heading", { name: "Deletar Despesa" })).not.toBeInTheDocument();
    });

    await waitFor(() =>
      expect(expenseRequests).toBeGreaterThan(requestsBeforeDelete),
    );
  });

  it("opens and closes the expense detail sheet", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({ items: [mockExpense], count: 1 }),
      ),
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(mockExpense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );

    const user = userEvent.setup();
    render(<WeddingFinancesView weddingUuid="w-1" />);

    await user.click(
      await screen.findByRole("button", { name: "Detalhar mock" }),
    );
    expect(
      await screen.findByRole("heading", { name: /Buffet Premium/i }),
    ).toBeInTheDocument();
    await user.click(screen.getByRole("button", { name: "Close" }));
    expect(
      screen.queryByRole("heading", { name: /Buffet Premium/i }),
    ).not.toBeInTheDocument();
  });
});
