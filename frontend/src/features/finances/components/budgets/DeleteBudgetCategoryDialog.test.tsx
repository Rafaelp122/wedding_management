import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { DeleteBudgetCategoryDialog } from "@/features/finances/components/budgets/DeleteBudgetCategoryDialog";
import { createMockBudgetCategory } from "@/test-data";
import { server } from "@/mocks/server";

import { toast } from "sonner";

describe("DeleteBudgetCategoryDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <DeleteBudgetCategoryDialog
        category={createMockBudgetCategory({ total_spent: "0" })}
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Remover Categoria")).not.toBeInTheDocument();
  });

  it("renders category name when open", () => {
    render(
      <DeleteBudgetCategoryDialog
        category={createMockBudgetCategory({ name: "Buffet", total_spent: "0" })}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Remover Categoria")).toBeInTheDocument();
    expect(screen.getByText("Buffet")).toBeInTheDocument();
  });

  it("disables delete button when category has expenses", () => {
    render(
      <DeleteBudgetCategoryDialog
        category={createMockBudgetCategory({ total_spent: "1500.00" })}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByRole("button", { name: /remover/i })).toBeDisabled();
    expect(
      screen.getByText(/esta categoria possui/i),
    ).toBeInTheDocument();
  });

  it("allows delete and shows success when no expenses", async () => {
    const onSuccess = vi.fn();
    render(
      <DeleteBudgetCategoryDialog
        category={createMockBudgetCategory({ total_spent: "0" })}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /remover/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Categoria removida com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.delete("*/api/v1/finances/categories/:uuid/", () =>
        HttpResponse.json({ detail: "Erro" }, { status: 500 }),
      ),
    );

    render(
      <DeleteBudgetCategoryDialog
        category={createMockBudgetCategory({ total_spent: "0" })}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /remover/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
  });
});
