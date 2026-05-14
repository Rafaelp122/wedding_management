import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { WeddingExpensesTable } from "@/features/finances/components/expenses/ExpensesTable";
import { createMockExpense } from "@/test-data";

describe("WeddingExpensesTable", () => {
  it("shows empty state when no expenses", () => {
    render(
      <WeddingExpensesTable
        expenses={[]}
        weddingUuid="w-1"
        onExpenseUpdated={vi.fn()}
      />,
    );

    expect(
      screen.getByText(/nenhuma despesa registrada/i),
    ).toBeInTheDocument();
  });

  it("renders expense rows", () => {
    const expenses = [createMockExpense()];

    render(
      <WeddingExpensesTable
        expenses={expenses}
        weddingUuid="w-1"
        onExpenseUpdated={vi.fn()}
      />,
    );

    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText("Parcial")).toBeInTheDocument();
  });
});
