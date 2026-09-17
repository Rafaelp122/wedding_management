import { describe, expect, it, vi } from "vitest";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { SignContractDialog } from "./SignContractDialog";
import { createMockContract } from "@/test-data";

describe("SignContractDialog", () => {
  const mockContract = createMockContract({
    uuid: "contract-123",
    name: "Contrato de Decoração",
    status: "DRAFT",
  });

  it("renders correctly with contract name and default today date", () => {
    render(
      <SignContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={vi.fn()}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Formalizar Assinatura")).toBeInTheDocument();
    expect(screen.getByText(/Contrato de Decoração/)).toBeInTheDocument();
    expect(screen.getByLabelText("Data da Assinatura")).toBeInTheDocument();
  });

  it("calls onOpenChange(false) when clicking Voltar", async () => {
    const onOpenChange = vi.fn();
    render(
      <SignContractDialog
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

  it("changes signed date and submits successfully", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/logistics/contracts/:uuid/sign/", () => {
        return HttpResponse.json({
          ...mockContract,
          status: "SIGNED",
          signed_date: "2026-09-20",
        });
      }),
    );

    render(
      <SignContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const dateInput = screen.getByLabelText("Data da Assinatura");
    await userEvent.clear(dateInput);
    await userEvent.type(dateInput, "2026-09-20");

    const submitBtn = screen.getByRole("button", { name: "Confirmar Assinatura" });
    await userEvent.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato assinado formalmente com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("shows error toast when mutation fails", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post("*/api/v1/logistics/contracts/:uuid/sign/", () => {
        return HttpResponse.json(
          { detail: "Contrato precisa de documento anexo." },
          { status: 422 },
        );
      }),
    );

    render(
      <SignContractDialog
        contract={mockContract}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const submitBtn = screen.getByRole("button", { name: "Confirmar Assinatura" });
    await userEvent.click(submitBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Contrato precisa de documento anexo.");
      expect(onOpenChange).not.toHaveBeenCalled();
      expect(onSuccess).not.toHaveBeenCalled();
    });
  });

  it("disables submit button and prevents action when contract is null", async () => {
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    render(
      <SignContractDialog
        contract={null}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const submitBtn = screen.getByRole("button", { name: "Confirmar Assinatura" });
    expect(submitBtn).toBeDisabled();
    await userEvent.click(submitBtn);

    expect(onOpenChange).not.toHaveBeenCalled();
  });
});
