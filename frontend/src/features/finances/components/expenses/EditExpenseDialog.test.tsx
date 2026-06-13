import { describe, expect, it, vi } from "vitest";
import { fireEvent, render, screen, userEvent, waitFor } from "@/test-utils";
import { EditExpenseDialog } from "@/features/finances/components/expenses/EditExpenseDialog";
import { createMockExpense } from "@/test-data";
import { server } from "@/mocks/server";

import { toast } from "sonner";

const mockExpense = createMockExpense({ paid_installments_count: 0 });

describe("EditExpenseDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Editar Despesa")).not.toBeInTheDocument();
  });

  it("renders with pre-filled data", () => {
    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Editar Despesa")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Despesa")).toHaveValue("Buffet Principal");
  });

  it("submits and shows success toast", async () => {
    const onSuccess = vi.fn();
    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Despesa atualizada com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("blocks amount fields when has paid installments", () => {
    render(
      <EditExpenseDialog
        expense={createMockExpense({ paid_installments_count: 2 })}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Valor Estimado")).toBeDisabled();
    expect(screen.getByLabelText("Valor Realizado")).toBeDisabled();
    expect(
      screen.getByText(/valores e parcelamento bloqueados/i),
    ).toBeInTheDocument();
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.patch("*/api/v1/finances/expenses/:uuid/", () =>
        HttpResponse.json({ detail: "Erro" }, { status: 500 }),
      ),
    );

    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
  });

  it("submits only changed fields", async () => {
    let requestBody: Record<string, unknown>;
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.patch(
        "*/api/v1/finances/expenses/:uuid/",
        async ({ request }) => {
          requestBody = (await request.json()) as Record<string, unknown>;
          return HttpResponse.json({ ...mockExpense, name: "Novo Nome" });
        },
      ),
    );

    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    const nameInput = screen.getByLabelText("Nome da Despesa");
    await user.clear(nameInput);
    await user.type(nameInput, "Novo Nome");

    await user.click(screen.getByRole("button", { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(requestBody).toEqual({ name: "Novo Nome" });
    });
  });

  it("sends num_installments when changed", async () => {
    let requestBody: Record<string, unknown>;
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.patch(
        "*/api/v1/finances/expenses/:uuid/",
        async ({ request }) => {
          requestBody = (await request.json()) as Record<string, unknown>;
          return HttpResponse.json({ ...mockExpense });
        },
      ),
    );

    render(
      <EditExpenseDialog
        expense={mockExpense}
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    const installmentsInput = screen.getByLabelText("Nº de Parcelas");
    fireEvent.change(installmentsInput, { target: { value: "5" } });

    await user.click(screen.getByRole("button", { name: /salvar alterações/i }));

    await waitFor(() => {
      expect(requestBody).toHaveProperty("num_installments", 5);
    });
  });
});
