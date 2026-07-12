/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { ExpenseDetailSheet } from "./ExpenseDetailSheet";
import { createMockExpense } from "@/test-data";

vi.mock("./ExpenseInstallmentRow", () => ({
  ExpenseInstallmentRow: ({ installment }: { installment: { installment_number: number } }) => (
    <tr data-testid="expense-installment-row">
      <td>{installment.installment_number}</td>
    </tr>
  ),
}));

vi.mock("./ExpenseRedistributeForm", () => ({
  ExpenseRedistributeForm: () => (
    <div data-testid="expense-redistribute-form" />
  ),
}));

import { useFinancesInstallmentsList } from "@/api/generated/v1/endpoints/finances/finances";

describe("ExpenseDetailSheet", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default MSW handlers
    vi.mocked(useFinancesInstallmentsList).mockReturnValue({
      data: { data: { items: [], count: 0 } },
      isLoading: false,
    } as any);
  });

  it("renders expense name in the sheet title", () => {
    const expense = createMockExpense({ name: "Buffet Principal" });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
  });

  it("shows category name", () => {
    const expense = createMockExpense({ category_name: "Buffet" });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText("Buffet")).toBeInTheDocument();
    expect(screen.getByText(/categoria:/i)).toBeInTheDocument();
  });

  it("shows contract description when present", () => {
    const expense = createMockExpense({
      contract_description: "Buffet Contrato 2025",
    });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText(/contrato:/i)).toBeInTheDocument();
    expect(screen.getByText("Buffet Contrato 2025")).toBeInTheDocument();
  });

  it("shows status badge", () => {
    const expense = createMockExpense({ status: "PARTIALLY_PAID" });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText("Parcial")).toBeInTheDocument();
  });

  it("shows progress bar with paid/total counts", () => {
    const expense = createMockExpense({
      paid_installments_count: 1,
      installments_count: 3,
      total_paid: "1500.00",
      actual_amount: "4800.00",
    });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(screen.getByText(/1\/3 marcadas como pagas/i)).toBeInTheDocument();

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it('shows "Remanejar" button when no installments are paid and toggles redistribute form', async () => {
    const expense = createMockExpense({ paid_installments_count: 0 });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    const remanejarBtn = screen.getByRole("button", { name: /remanejar/i });
    expect(remanejarBtn).toBeInTheDocument();

    expect(
      screen.queryByTestId("expense-redistribute-form"),
    ).not.toBeInTheDocument();

    await user.click(remanejarBtn);
    expect(
      screen.getByTestId("expense-redistribute-form"),
    ).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /remanejar/i }));
    expect(
      screen.queryByTestId("expense-redistribute-form"),
    ).not.toBeInTheDocument();
  });

  it('hides "Remanejar" when installments are paid', () => {
    const expense = createMockExpense({ paid_installments_count: 1 });
    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
    );

    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    expect(
      screen.queryByRole("button", { name: /remanejar/i }),
    ).not.toBeInTheDocument();
  });

  it("shows loading skeleton when installments are loading", () => {
    vi.mocked(useFinancesInstallmentsList).mockReturnValue({
      data: undefined,
      isLoading: true,
    } as any);

    render(
      <ExpenseDetailSheet
        expense={createMockExpense()}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      document.body.querySelector(".animate-pulse"),
    ).toBeInTheDocument();

    expect(
      screen.queryByText("Nenhuma parcela encontrada."),
    ).not.toBeInTheDocument();

    expect(
      screen.queryByTestId("expense-installment-row"),
    ).not.toBeInTheDocument();
  });

  it('shows "Nenhuma parcela encontrada" when installments are empty', async () => {
    // Default MSW handler returns empty installments
    render(
      <ExpenseDetailSheet
        expense={createMockExpense()}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    await waitFor(() => {
      expect(
        screen.getByText("Nenhuma parcela encontrada."),
      ).toBeInTheDocument();
    });
  });
});
