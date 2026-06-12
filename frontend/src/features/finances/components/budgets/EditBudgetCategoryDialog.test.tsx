import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { EditBudgetCategoryDialog } from "@/features/finances/components/budgets/EditBudgetCategoryDialog";
import { createMockBudgetCategory } from "@/test-data";

import { toast } from "sonner";

const mockCategory = createMockBudgetCategory({
  uuid: "cat-1",
  name: "Buffet",
  allocated_budget: "5000.00",
  total_spent: "3200.00",
});

describe("EditBudgetCategoryDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <EditBudgetCategoryDialog
        category={mockCategory}
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Editar Categoria")).not.toBeInTheDocument();
  });

  it("renders with pre-filled data", () => {
    render(
      <EditBudgetCategoryDialog
        category={mockCategory}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Editar Categoria")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("Buffet");
  });

  it("shows warning when new value is below total spent", async () => {
    render(
      <EditBudgetCategoryDialog
        category={mockCategory}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const valueInput = screen.getByLabelText("Valor Orçado (R$)");
    const user = userEvent.setup();
    await user.clear(valueInput);
    await user.type(valueInput, "1000");

    await waitFor(() => {
      expect(
        screen.getByText(/o novo valor é menor que o total já gasto/i),
      ).toBeInTheDocument();
    });
  });

  it("submits and shows success toast", async () => {
    const onSuccess = vi.fn();
    render(
      <EditBudgetCategoryDialog
        category={mockCategory}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Categoria atualizada com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
