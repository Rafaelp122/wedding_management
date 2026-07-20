import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { DeleteExpenseDialog } from "@/features/finances/components/expenses/DeleteExpenseDialog";
import { server } from "@/mocks/server";
import { createMockExpense } from "@/test-data";

import { toast } from "sonner";

const mockExpense = createMockExpense();

describe("DeleteExpenseDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <DeleteExpenseDialog
        expense={mockExpense}
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Deletar Despesa")).not.toBeInTheDocument();
  });

  it("renders expense name when open", () => {
    render(
      <DeleteExpenseDialog
        expense={mockExpense}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Deletar Despesa")).toBeInTheDocument();
    expect(screen.getByText("Buffet Principal")).toBeInTheDocument();
  });

  it.each([
    [createMockExpense({ name: undefined, description: "Decoração floral" }), "Decoração floral"],
    [createMockExpense({ name: undefined, description: undefined, uuid: "expense-fallback" }), "expense-fallback"],
  ])("uses the available expense identifier", (expense, identifier) => {
    render(
      <DeleteExpenseDialog
        expense={expense}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText(identifier)).toBeInTheDocument();
  });

  it("calls onSuccess after successful delete", async () => {
    const onSuccess = vi.fn();
    render(
      <DeleteExpenseDialog
        expense={mockExpense}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText(/digite o nome aqui/i),
      "Buffet Principal",
    );
    await user.click(
      screen.getByRole("button", { name: /deletar permanentemente/i }),
    );

    await waitFor(
      () => {
        expect(toast.success).toHaveBeenCalledWith(
          "Despesa deletada com sucesso!",
        );
        expect(onSuccess).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.delete("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json({ detail: "Erro ao deletar" }, { status: 500 }),
      ),
    );

    render(
      <DeleteExpenseDialog
        expense={mockExpense}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText(/digite o nome aqui/i),
      "Buffet Principal",
    );
    await user.click(
      screen.getByRole("button", { name: /deletar permanentemente/i }),
    );

    await waitFor(
      () => {
        expect(toast.error).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });
});
