import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { CreateBudgetCategoryDialog } from "@/features/finances/components/budgets/CreateBudgetCategoryDialog";

describe("CreateBudgetCategoryDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <CreateBudgetCategoryDialog
        weddingUuid="w-1"
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Nova Categoria")).not.toBeInTheDocument();
  });

  it("renders form fields when open", () => {
    render(
      <CreateBudgetCategoryDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Nova Categoria")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("Valor Orçado (R$)")).toBeInTheDocument();
  });

  it("submit button is disabled until budget loads", () => {
    render(
      <CreateBudgetCategoryDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /criar categoria/i })).toBeDisabled();
  });

  it("enables submit button after budget loads", async () => {
    render(
      <CreateBudgetCategoryDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /criar categoria/i })).not.toBeDisabled();
    });
  });

  it("shows validation error on empty submit", async () => {
    render(
      <CreateBudgetCategoryDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /criar categoria/i })).not.toBeDisabled();
    });

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /criar categoria/i }));

    await screen.findByText(/invalid/i);
  });
});
