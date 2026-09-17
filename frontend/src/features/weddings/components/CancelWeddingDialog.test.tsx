import { describe, expect, it, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { CancelWeddingDialog } from "./CancelWeddingDialog";
import { createMockWedding } from "@/test-data";

describe("CancelWeddingDialog", () => {
  const mockWedding = createMockWedding({
    uuid: "wedding-123",
    groom_name: "Lucas",
    bride_name: "Mariana",
    status: "IN_PROGRESS",
  });

  it("renders correctly with couple names and alert description", () => {
    render(
      <CancelWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Cancelar Casamento")).toBeInTheDocument();
    expect(screen.getByText(/Lucas & Mariana/)).toBeInTheDocument();
    expect(
      screen.getByText(/O status do casamento será alterado para/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Confirmar Cancelamento" }),
    ).toBeInTheDocument();
  });

  it("calls onOpenChange(false) when clicking Voltar", async () => {
    const onOpenChange = vi.fn();
    render(
      <CancelWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />,
    );

    const backBtn = screen.getByRole("button", { name: "Voltar" });
    await userEvent.click(backBtn);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("submits cancellation successfully, closes dialog and invokes onSuccess", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/weddings/:uuid/cancel/", () => {
        return HttpResponse.json({
          ...mockWedding,
          status: "CANCELED",
        });
      }),
    );

    render(
      <CancelWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const confirmBtn = screen.getByRole("button", {
      name: "Confirmar Cancelamento",
    });
    await userEvent.click(confirmBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Casamento cancelado com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("shows error toast when cancellation mutation fails", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/weddings/:uuid/cancel/", () => {
        return HttpResponse.json(
          { detail: "Casamento já concluído ou inválido." },
          { status: 422 },
        );
      }),
    );

    render(
      <CancelWeddingDialog
        wedding={mockWedding}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const confirmBtn = screen.getByRole("button", {
      name: "Confirmar Cancelamento",
    });
    await userEvent.click(confirmBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Casamento já concluído ou inválido.",
      );
      expect(onOpenChange).not.toHaveBeenCalledWith(false);
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });
});
