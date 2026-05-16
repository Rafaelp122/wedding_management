import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { CreateExpenseDialog } from "@/features/finances/components/expenses/CreateExpenseDialog";

describe("CreateExpenseDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <CreateExpenseDialog
        weddingUuid="w-1"
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Nova Despesa")).not.toBeInTheDocument();
  });

  it("renders form fields when open", () => {
    render(
      <CreateExpenseDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Nova Despesa")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Despesa")).toBeInTheDocument();
    expect(screen.getByLabelText("Categoria")).toBeInTheDocument();
    expect(screen.getByLabelText("Valor Estimado")).toBeInTheDocument();
    expect(screen.getByLabelText("Nº de Parcelas")).toBeInTheDocument();
  });

  it("shows validation error on empty submit", async () => {
    render(
      <CreateExpenseDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /criar despesa/i }));

    const errors = await screen.findAllByText(/invalid/i);
    expect(errors.length).toBeGreaterThan(0);
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    render(
      <CreateExpenseDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
