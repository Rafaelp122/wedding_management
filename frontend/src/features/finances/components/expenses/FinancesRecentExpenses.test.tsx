import { describe, expect, it, vi } from "vitest";
import { render, screen, server, userEvent } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingFinancesRecentExpenses } from "./FinancesRecentExpenses";
import { createMockExpense } from "@/test-data";
import "./ExpenseDetailSheet";

describe("WeddingFinancesRecentExpenses", () => {
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

    expect(screen.getByText("Despesas Recentes")).toBeInTheDocument();

    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
    expect(screen.getByText("Decoração Luxo")).toBeInTheDocument();

    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("Decoração")).toBeInTheDocument();

    expect(screen.getByText(/R\$\s*4\.800/)).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*2\.500/)).toBeInTheDocument();

    expect(screen.getByText("Parcial")).toBeInTheDocument();
    expect(screen.getByText("Quitada")).toBeInTheDocument();

    expect(screen.getByText("1/3 parcelas")).toBeInTheDocument();
  });

  it("shows empty state when expenses is empty", () => {
    render(<WeddingFinancesRecentExpenses expenses={[]} />);

    expect(
      screen.getByText("Nenhuma despesa registrada no sistema."),
    ).toBeInTheDocument();
  });

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

  it("opens detail dialog when an expense card is clicked", async () => {
    const user = userEvent.setup();
    const expense = createMockExpense({ uuid: "e-1", name: "Buffet Premium" });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    await user.click(screen.getByText("Buffet Premium"));

    expect(
      await screen.findByRole("heading", { name: /Buffet Premium/i }),
    ).toBeInTheDocument();
  });

  it("closes dialog when close button is clicked", async () => {
    const user = userEvent.setup();
    const expense = createMockExpense({ uuid: "e-1", name: "Buffet Premium" });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    await user.click(screen.getByText("Buffet Premium"));
    expect(
      await screen.findByRole("heading", { name: /Buffet Premium/i }),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Close" }));

    expect(
      screen.queryByRole("heading", { name: /Buffet Premium/i }),
    ).not.toBeInTheDocument();
  });

  it('renders "N/A" fallback when name and description are empty', () => {
    const expense = createMockExpense({
      name: undefined,
      description: undefined,
    });

    render(<WeddingFinancesRecentExpenses expenses={[expense]} />);

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });
});
