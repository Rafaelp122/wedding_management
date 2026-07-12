/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, waitFor, server } from "@/test-utils";
import { http, HttpResponse } from "msw";

import { ExpenseRedistributeForm } from "./ExpenseRedistributeForm";

const EXPENSE_UUID = "test-expense-uuid";

import { toast } from "sonner";

let capturedBody: unknown;

import { useFinancesExpensesUpdate } from "@/api/generated/v1/endpoints/finances/finances";

describe("ExpenseRedistributeForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    capturedBody = undefined;

    // Default: successful mutation via MSW
    server.use(
      http.patch(`*/api/v1/finances/expenses/${EXPENSE_UUID}/`, async ({ request }) => {
        capturedBody = await request.json();
        return HttpResponse.json({ uuid: EXPENSE_UUID, num_installments: 3 });
      }),
    );
  });

  it("renders with initial values from props", () => {
    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    expect(screen.getByDisplayValue("3")).toBeInTheDocument();
    expect(screen.getByDisplayValue("2025-07-15")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /aplicar/i }),
    ).toBeInTheDocument();
  });

  it("defaults first due date to today when firstExistingDate is null", () => {
    const today = new Date().toISOString().slice(0, 10);

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={1}
        firstExistingDate={null}
      />,
    );

    expect(screen.getByDisplayValue(today)).toBeInTheDocument();
    expect(screen.getByDisplayValue("1")).toBeInTheDocument();
  });

  it("changing nº de parcelas updates the input", async () => {
    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    const numInput = screen.getByDisplayValue("3");
    await user.tripleClick(numInput);
    await user.keyboard("6");

    expect(screen.getByDisplayValue("6")).toBeInTheDocument();
  });

  it("changing first due date updates the input", async () => {
    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    const dateInput = screen.getByDisplayValue("2025-07-15");
    await user.clear(dateInput);
    await user.type(dateInput, "2025-08-01");

    expect(screen.getByDisplayValue("2025-08-01")).toBeInTheDocument();
  });

  it("shows success toast on successful mutation", async () => {
    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    await user.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() => {
      expect(capturedBody).toMatchObject({
        num_installments: 3,
        first_due_date: "2025-07-15",
      });
      expect(toast.success).toHaveBeenCalledWith(
        "Parcelas remanejadas com sucesso!",
      );
    });
  });

  it("shows error toast on failed mutation", async () => {
    server.use(
      http.patch(`*/api/v1/finances/expenses/${EXPENSE_UUID}/`, async () => {
        return HttpResponse.json({ detail: "API Error" }, { status: 400 });
      }),
    );

    const user = userEvent.setup();

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    await user.click(screen.getByRole("button", { name: /aplicar/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("API Error");
    });
  });

  it("button is disabled while mutation is pending", () => {
    vi.mocked(useFinancesExpensesUpdate).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: true,
    } as any);

    render(
      <ExpenseRedistributeForm
        expenseUuid={EXPENSE_UUID}
        currentCount={3}
        firstExistingDate="2025-07-15"
      />,
    );

    expect(
      screen.getByRole("button", { name: /aplicar/i }),
    ).toBeDisabled();
  });
});
