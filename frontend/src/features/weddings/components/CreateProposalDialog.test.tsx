import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { CreateProposalDialog } from "./CreateProposalDialog";
import { toast } from "sonner";

describe("CreateProposalDialog", () => {
  it("renders nothing when closed", () => {
    render(
      <CreateProposalDialog
        open={false}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Nova Proposta de Casamento"),
    ).not.toBeInTheDocument();
  });

  it("renders all form fields when open", () => {
    render(
      <CreateProposalDialog
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(
      screen.getByText("Nova Proposta de Casamento"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Nome do Noivo")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Noiva")).toBeInTheDocument();
    expect(screen.getByLabelText("Data Estimada")).toBeInTheDocument();
    expect(screen.getByLabelText("Local Previsto")).toBeInTheDocument();
    expect(screen.getByLabelText("Convidados Estimados")).toBeInTheDocument();
    expect(screen.getByLabelText("Modelo de Cronograma")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome do Contratante")).toBeInTheDocument();
    expect(screen.getByLabelText("CPF do Contratante")).toBeInTheDocument();
    expect(screen.getByLabelText("Papel / Relação")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail do Contratante")).toBeInTheDocument();
    expect(screen.getByLabelText("Telefone / WhatsApp")).toBeInTheDocument();
  });

  it("shows validation error when required fields are empty", async () => {
    render(
      <CreateProposalDialog
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    const submitBtn = screen.getByRole("button", {
      name: /criar proposta/i,
    });
    await user.click(submitBtn);

    expect(
      await screen.findByText("Nome do noivo é obrigatório"),
    ).toBeInTheDocument();
    expect(
      await screen.findByText("Nome da noiva é obrigatório"),
    ).toBeInTheDocument();
  });

  it("submits valid proposal form and triggers success callback", async () => {
    const onSuccess = vi.fn();
    const onOpenChange = vi.fn();

    render(
      <CreateProposalDialog
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome do Noivo"), "Bruno Rocha");
    await user.type(screen.getByLabelText("Nome da Noiva"), "Camila Alves");
    await user.type(screen.getByLabelText("Data Estimada"), "2026-11-20");
    await user.type(screen.getByLabelText("Local Previsto"), "Espaço das Palmeiras");
    await user.type(screen.getByLabelText("Nome do Contratante"), "Bruno Rocha");

    const submitBtn = screen.getByRole("button", {
      name: /criar proposta/i,
    });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Proposta criada com sucesso!",
      );
      expect(onOpenChange).toHaveBeenCalledWith(false);
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
