import { describe, expect, it, vi, beforeEach } from "vitest";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { CreateAddendumDialog } from "./CreateAddendumDialog";
import { createMockContractAddendum } from "@/test-data";

describe("CreateAddendumDialog", () => {
  const CONTRACT_ID = "contract-123";

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("renderiza campos de valor e justificativa corretamente", () => {
    render(
      <CreateAddendumDialog
        contractUuid={CONTRACT_ID}
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByText("Novo Termo Aditivo")).toBeInTheDocument();
    expect(screen.getByLabelText(/Valor do Aditivo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Justificativa do Aditivo/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Criar Aditivo" })).toBeInTheDocument();
  });

  it("não permite envio quando valor é zero ou justificativa está vazia", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    render(
      <CreateAddendumDialog
        contractUuid={CONTRACT_ID}
        open={true}
        onOpenChange={onOpenChange}
      />,
    );

    const submitBtn = screen.getByRole("button", { name: "Criar Aditivo" });
    await user.click(submitBtn);

    expect(
      await screen.findByText("O valor do aditivo deve ser positivo"),
    ).toBeInTheDocument();
    expect(
      screen.getByText("A justificativa é obrigatória"),
    ).toBeInTheDocument();
    expect(onOpenChange).not.toHaveBeenCalled();
  });

  it("cria aditivo com sucesso, exibe toast e fecha o modal", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();
    const onSuccess = vi.fn();

    const createdAddendum = createMockContractAddendum({
      contract_id: CONTRACT_ID,
      amount: "1500.00",
      justification: "Inclusão de DJ e iluminação",
    });

    server.use(
      http.post("*/api/v1/contracts/:contractId/addendums/", () => {
        return HttpResponse.json(createdAddendum);
      }),
    );

    render(
      <CreateAddendumDialog
        contractUuid={CONTRACT_ID}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const amountInput = screen.getByLabelText(/Valor do Aditivo/i);
    const justificationInput = screen.getByLabelText(/Justificativa do Aditivo/i);

    await user.clear(amountInput);
    await user.type(amountInput, "1500");
    await user.type(justificationInput, "Inclusão de DJ e iluminação");

    const submitBtn = screen.getByRole("button", { name: "Criar Aditivo" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Termo aditivo criado com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });

  it("exibe mensagem de erro quando a chamada da API falha", async () => {
    const user = userEvent.setup();
    const onOpenChange = vi.fn();

    server.use(
      http.post("*/api/v1/contracts/:contractId/addendums/", () => {
        return HttpResponse.json(
          { detail: "Contrato não aceita novos aditivos neste status." },
          { status: 400 },
        );
      }),
    );

    render(
      <CreateAddendumDialog
        contractUuid={CONTRACT_ID}
        open={true}
        onOpenChange={onOpenChange}
      />,
    );

    const amountInput = screen.getByLabelText(/Valor do Aditivo/i);
    const justificationInput = screen.getByLabelText(/Justificativa do Aditivo/i);

    await user.clear(amountInput);
    await user.type(amountInput, "2000");
    await user.type(justificationInput, "Acréscimo de bebidas premium");

    const submitBtn = screen.getByRole("button", { name: "Criar Aditivo" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Contrato não aceita novos aditivos neste status.",
      );
      expect(onOpenChange).not.toHaveBeenCalled();
    });
  });
});
