import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { ExpenseDetailSheet } from "./ExpenseDetailSheet";
import { createMockExpense, createMockInstallment } from "@/test-data";

vi.mock("./ExpenseInstallmentRow", () => ({
  ExpenseInstallmentRow: ({
    installment,
    onTogglePayment,
    isPaying,
  }: {
    installment: { uuid: string; installment_number: number; status: string };
    onTogglePayment: (uuid: string, isPaid: boolean) => void;
    isPaying: boolean;
  }) => {
    const isPaid = installment.status === "PAID";
    return (
      <tr data-testid="expense-installment-row">
        <td>{installment.installment_number}</td>
        <td>
          <button
            onClick={() => onTogglePayment(installment.uuid, isPaid)}
            disabled={isPaying}
          >
            {isPaid ? "Desmarcar" : "Marcar como Pago"}
          </button>
        </td>
      </tr>
    );
  },
}));

vi.mock("./ExpenseRedistributeForm", () => ({
  ExpenseRedistributeForm: () => (
    <div data-testid="expense-redistribute-form" />
  ),
}));

describe("ExpenseDetailSheet", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Default MSW handlers
    server.use(
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0 }),
      ),
    );
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
    server.use(
      http.get("*/api/v1/finances/installments/", () => new Promise(() => {})),
    );

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

  it("allows marking an installment as paid successfully", async () => {
    const expense = createMockExpense({ uuid: "exp-1" });
    const installment = createMockInstallment({
      uuid: "inst-1",
      installment_number: 1,
      status: "PENDING",
    });

    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [installment], count: 1 }),
      ),
      http.post("*/api/v1/finances/installments/:uuid/mark-as-paid/", () => {
        return HttpResponse.json(installment, { status: 200 });
      }),
    );

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // Click "Marcar como Pago" button
    const payBtn = await screen.findByRole("button", { name: "Marcar como Pago" });
    await user.click(payBtn);

    // Verify success toast and reload
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Parcela marcada como paga!");
    });
  });

  it("allows unmarking an installment as paid successfully", async () => {
    const expense = createMockExpense({ uuid: "exp-1" });
    const installment = createMockInstallment({
      uuid: "inst-1",
      installment_number: 1,
      status: "PAID",
    });

    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [installment], count: 1 }),
      ),
      http.post("*/api/v1/finances/installments/:uuid/unmark-as-paid/", () => {
        return HttpResponse.json(installment, { status: 200 });
      }),
    );

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // Click "Desmarcar" button
    const unpayBtn = await screen.findByRole("button", { name: "Desmarcar" });
    await user.click(unpayBtn);

    // Verify success toast and reload
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Parcela desmarcada como paga.");
    });
  });

  it("shows error toast when marking installment fails", async () => {
    const expense = createMockExpense({ uuid: "exp-1" });
    const installment = createMockInstallment({
      uuid: "inst-1",
      installment_number: 1,
      status: "PENDING",
    });

    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [installment], count: 1 }),
      ),
      http.post("*/api/v1/finances/installments/:uuid/mark-as-paid/", () => {
        return HttpResponse.json({ detail: "Operação inválida" }, { status: 400 });
      }),
    );

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // Click "Marcar como Pago" button
    const payBtn = await screen.findByRole("button", { name: "Marcar como Pago" });
    await user.click(payBtn);

    // Verify error toast has API error message
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Operação inválida");
    });
  });

  it("shows fallback error toast when unmarking installment fails without message detail", async () => {
    const expense = createMockExpense({ uuid: "exp-1" });
    const installment = createMockInstallment({
      uuid: "inst-1",
      installment_number: 1,
      status: "PAID",
    });

    server.use(
      http.get("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json(expense),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [installment], count: 1 }),
      ),
      http.post("*/api/v1/finances/installments/:uuid/unmark-as-paid/", () => {
        return new HttpResponse(null, { status: 500 });
      }),
    );

    const user = userEvent.setup();
    render(
      <ExpenseDetailSheet expense={expense} open={true} onOpenChange={vi.fn()} />,
    );

    // Click "Desmarcar" button
    const unpayBtn = await screen.findByRole("button", { name: "Desmarcar" });
    await user.click(unpayBtn);

    // Verify fallback error toast
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro ao desmarcar parcela.");
    });
  });
});
