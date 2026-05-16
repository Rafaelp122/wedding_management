import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { DeleteWeddingDialog } from "@/features/weddings/components/DeleteWeddingDialog";
import { server } from "@/mocks/server";
import { createMockWedding } from "@/test-data";

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

const mockWedding = createMockWedding();

describe("DeleteWeddingDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <DeleteWeddingDialog
        wedding={mockWedding}
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Deletar Casamento"),
    ).not.toBeInTheDocument();
  });

  it("renders delete confirmation when open", () => {
    render(
      <DeleteWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Deletar Casamento")).toBeInTheDocument();
    expect(
      screen.getByText(/João Silva & Maria Souza/),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Orçamentos e categorias/),
    ).toBeInTheDocument();
  });

  it("delete button is disabled until name is typed", () => {
    render(
      <DeleteWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const deleteBtn = screen.getByRole("button", {
      name: /deletar permanentemente/i,
    });
    expect(deleteBtn).toBeDisabled();
  });

  it("calls onSuccess after successful delete", async () => {
    const onSuccess = vi.fn();
    render(
      <DeleteWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText(/digite o nome aqui/i),
      "João Silva & Maria Souza",
    );
    await user.click(
      screen.getByRole("button", { name: /deletar permanentemente/i }),
    );

    await waitFor(
      () => {
        expect(toastSuccess).toHaveBeenCalledWith(
          "Casamento deletado com sucesso!",
        );
        expect(onSuccess).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.delete("*/api/v1/weddings/:uuid/", () =>
        HttpResponse.json({ detail: "Não foi possível deletar" }, { status: 500 }),
      ),
    );

    render(
      <DeleteWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(
      screen.getByPlaceholderText(/digite o nome aqui/i),
      "João Silva & Maria Souza",
    );
    await user.click(
      screen.getByRole("button", { name: /deletar permanentemente/i }),
    );

    await waitFor(
      () => {
        expect(toastError).toHaveBeenCalled();
      },
      { timeout: 5000 },
    );
  });
});
