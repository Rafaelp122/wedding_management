import { describe, expect, it, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { CancelContractDialog } from "./CancelContractDialog";
import { createMockContract } from "@/test-data";

describe("CancelContractDialog", () => {
  const mockContract = createMockContract({
    uuid: "contract-456",
    name: "Contrato de Buffet",
    status: "SIGNED",
  });

  it("renders correctly with contract name and warning details", () => {
    render(
      <CancelContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Cancelar Contrato")).toBeInTheDocument();
    expect(screen.getByText(/Contrato de Buffet/)).toBeInTheDocument();
    expect(
      screen.getByText(/Os itens logísticos vinculados permanecerão associados com histórico/),
    ).toBeInTheDocument();
  });

  it("calls onOpenChange(false) when clicking Voltar", async () => {
    const onOpenChange = vi.fn();
    render(
      <CancelContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={vi.fn()}
      />,
    );

    const backBtn = screen.getByRole("button", { name: "Voltar" });
    await userEvent.click(backBtn);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("confirms cancellation and calls mutation successfully", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/logistics/contracts/:uuid/cancel/", () => {
        return HttpResponse.json({
          ...mockContract,
          status: "CANCELLED",
        });
      }),
    );

    render(
      <CancelContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const confirmBtn = screen.getByRole("button", { name: "Confirmar Cancelamento" });
    await userEvent.click(confirmBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato cancelado com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("shows error toast when cancellation mutation fails", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/logistics/contracts/:uuid/cancel/", () => {
        return HttpResponse.json(
          { detail: "Contrato não pode ser cancelado neste estado." },
          { status: 422 },
        );
      }),
    );

    render(
      <CancelContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const confirmBtn = screen.getByRole("button", { name: "Confirmar Cancelamento" });
    await userEvent.click(confirmBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Contrato não pode ser cancelado neste estado.");
      expect(onOpenChange).not.toHaveBeenCalled();
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  it("disables confirm button when contract is null", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    render(
      <CancelContractDialog
        contract={null}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const confirmBtn = screen.getByRole("button", { name: "Confirmar Cancelamento" });
    expect(confirmBtn).toBeDisabled();
    await userEvent.click(confirmBtn);

    expect(onOpenChange).not.toHaveBeenCalled();
  });
});
