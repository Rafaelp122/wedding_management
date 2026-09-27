import { describe, expect, it, vi, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { SignAddendumDialog } from "./SignAddendumDialog";
import { createMockContractAddendum } from "@/test-data";

describe("SignAddendumDialog", () => {
  const CONTRACT_ID = "contract-123";
  const mockAddendum = createMockContractAddendum({
    uuid: "addendum-456",
    contract_id: CONTRACT_ID,
    amount: "2500.00",
    justification: "Inclusão de iluminação cênica",
    status: "PENDING",
  });

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renderiza corretamente com valor, justificativa e campo de data", () => {
    render(
      <SignAddendumDialog
        contractUuid={CONTRACT_ID}
        addendum={mockAddendum}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Formalizar Assinatura do Aditivo")).toBeInTheDocument();
    expect(screen.getByText(/2\.500,00/)).toBeInTheDocument();
    expect(screen.getByText(/Inclusão de iluminação cênica/)).toBeInTheDocument();
    expect(screen.getByLabelText("Data da Assinatura")).toBeInTheDocument();
  });

  it("chama onOpenChange(false) ao clicar no botão Voltar", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(
      <SignAddendumDialog
        contractUuid={CONTRACT_ID}
        addendum={mockAddendum}
        open={true}
        onOpenChange={onOpenChange}
      />,
    );

    const backBtn = screen.getByRole("button", { name: "Voltar" });
    await user.click(backBtn);

    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("formaliza assinatura com sucesso, exibe toast e fecha o modal", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    server.use(
      http.post(
        "*/api/v1/contracts/:contractId/addendums/:addendumId/sign/",
        () => {
          return HttpResponse.json({
            ...mockAddendum,
            status: "SIGNED",
            signed_date: "2026-09-21",
          });
        },
      ),
    );

    render(
      <SignAddendumDialog
        contractUuid={CONTRACT_ID}
        addendum={mockAddendum}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const dateInput = screen.getByLabelText("Data da Assinatura");
    await user.clear(dateInput);
    await user.type(dateInput, "2026-09-21");

    const submitBtn = screen.getByRole("button", { name: "Confirmar Assinatura" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Aditivo assinado com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("exibe mensagem de erro quando a chamada à API falha", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    server.use(
      http.post(
        "*/api/v1/contracts/:contractId/addendums/:addendumId/sign/",
        () => {
          return HttpResponse.json(
            { detail: "Aditivo já assinado ou inválido." },
            { status: 400 },
          );
        },
      ),
    );

    render(
      <SignAddendumDialog
        contractUuid={CONTRACT_ID}
        addendum={mockAddendum}
        open={true}
        onOpenChange={onOpenChange}
      />,
    );

    const submitBtn = screen.getByRole("button", { name: "Confirmar Assinatura" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Aditivo já assinado ou inválido.");
      expect(onOpenChange).not.toHaveBeenCalled();
    });
  });
});
