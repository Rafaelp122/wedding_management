import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { WeddingExpensesTable } from "@/features/finances/components/expenses/ExpensesTable";
import { createMockExpense } from "@/test-data";

describe("WeddingExpensesTable", () => {
  it("shows empty state when no expenses", () => {
    render(
      <WeddingExpensesTable
        expenses={[]}
        onEditExpense={vi.fn()}
        onDeleteExpense={vi.fn()}
        onDetailExpense={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/nenhuma despesa registrada/i),
    ).toBeInTheDocument();
  });

  it("renders expense rows correctly", () => {
    const expenses = [
      createMockExpense({
        uuid: "e-1",
        name: "Expense 1",
        category_name: "Buffet",
        status: "SETTLED",
      }),
    ];

    render(
      <WeddingExpensesTable
        expenses={expenses}
        onEditExpense={vi.fn()}
        onDeleteExpense={vi.fn()}
        onDetailExpense={vi.fn()}
      />,
    );

    expect(screen.getByText("Expense 1")).toBeInTheDocument();
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("Quitada")).toBeInTheDocument();
  });

  it("triggers callbacks for actions", async () => {
    const expenses = [createMockExpense({ name: "Buffet Principal" })];
    const onEditExpense = vi.fn();
    const onDeleteExpense = vi.fn();
    const onDetailExpense = vi.fn();
    const user = userEvent.setup();

    render(
      <WeddingExpensesTable
        expenses={expenses}
        onEditExpense={onEditExpense}
        onDeleteExpense={onDeleteExpense}
        onDetailExpense={onDetailExpense}
      />,
    );

    // Click expense name to trigger detail view
    const nameBtn = screen.getByRole("button", { name: "Buffet Principal" });
    await user.click(nameBtn);
    expect(onDetailExpense).toHaveBeenCalledWith(expenses[0]);

    // Open dropdown menu
    const menuBtn = screen.getByRole("button", { name: /ações da despesa/i });
    await user.click(menuBtn);

    // Click edit
    const editBtn = screen.getByText("Editar");
    await user.click(editBtn);
    expect(onEditExpense).toHaveBeenCalledWith(expenses[0]);

    // Open dropdown menu again to click delete
    await user.click(menuBtn);
    const deleteBtn = screen.getByText("Excluir");
    await user.click(deleteBtn);
    expect(onDeleteExpense).toHaveBeenCalledWith(expenses[0]);
  });

  it("renders tooltip for expense name", async () => {
    const expenses = [createMockExpense({ name: "Despesa Longa " + "A".repeat(50) })];
    const user = userEvent.setup();

    render(
      <WeddingExpensesTable
        expenses={expenses}
        onEditExpense={vi.fn()}
        onDeleteExpense={vi.fn()}
        onDetailExpense={vi.fn()}
      />,
    );

    const nameBtn = screen.getByRole("button", { name: /despesa longa/i });
    await user.hover(nameBtn);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: expenses[0].name })).toBeInTheDocument();
    });
  });

  it("renders tooltip for actions menu button", async () => {
    const expenses = [createMockExpense()];
    const user = userEvent.setup();

    render(
      <WeddingExpensesTable
        expenses={expenses}
        onEditExpense={vi.fn()}
        onDeleteExpense={vi.fn()}
        onDetailExpense={vi.fn()}
      />,
    );

    const actionsBtn = screen.getByRole("button", { name: /ações da despesa/i });
    await user.hover(actionsBtn);
    await waitFor(() => {
      expect(screen.getByRole("tooltip", { name: "Ações da despesa" })).toBeInTheDocument();
    });
  });
});
