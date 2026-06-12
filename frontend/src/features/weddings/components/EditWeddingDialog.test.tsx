import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { EditWeddingDialog } from "@/features/weddings/components/EditWeddingDialog";
import { server } from "@/mocks/server";
import { createMockWedding } from "@/test-data";
import { toast } from "sonner";

const mockWedding = createMockWedding();

describe("EditWeddingDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <EditWeddingDialog
        wedding={mockWedding}
        open={false}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.queryByText("Editar Casamento")).not.toBeInTheDocument();
  });

  it("renders dialog with pre-filled data", () => {
    render(
      <EditWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Editar Casamento")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome do Noivo")).toHaveValue("João Silva");
    expect(screen.getByLabelText("Nome da Noiva")).toHaveValue("Maria Souza");
    expect(screen.getByLabelText("Local")).toHaveValue("São Paulo");
    expect(screen.getByLabelText("Data do Casamento")).toHaveValue("2025-06-15");
  });

  it("submits and shows success toast", async () => {
    const onSuccess = vi.fn();
    render(
      <EditWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    const groomInput = screen.getByLabelText("Nome do Noivo");
    await user.clear(groomInput);
    await user.type(groomInput, "Carlos Updated");
    await user.click(
      screen.getByRole("button", { name: /salvar alterações/i }),
    );

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Casamento atualizado com sucesso!",
      );
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    render(
      <EditWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.patch("*/api/v1/weddings/:uuid/", () =>
        HttpResponse.json({ detail: "Erro ao atualizar" }, { status: 500 }),
      ),
    );

    render(
      <EditWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(
      screen.getByRole("button", { name: /salvar alterações/i }),
    );

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    });
  });
});
