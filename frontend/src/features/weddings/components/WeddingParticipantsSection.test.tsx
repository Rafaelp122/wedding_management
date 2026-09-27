import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@/test-utils";
import { WeddingParticipantsSection } from "./WeddingParticipantsSection";
import { createMockWeddingParticipant } from "@/test-data";

describe("WeddingParticipantsSection (Dumb Component)", () => {
  it("renderiza mensagem de estado vazio quando não há participantes", () => {
    const handleAdd = vi.fn();
    render(
      <WeddingParticipantsSection
        participants={[]}
        onAddParticipant={handleAdd}
      />
    );

    expect(screen.getByText("Participantes & Contratantes")).toBeInTheDocument();
    expect(
      screen.getByText("Nenhum participante adicional vinculado.")
    ).toBeInTheDocument();

    const addBtn = screen.getByRole("button", { name: /vincular participante/i });
    fireEvent.click(addBtn);
    expect(handleAdd).toHaveBeenCalledTimes(1);
  });

  it("renderiza lista de participantes com badges e contatos", () => {
    const participant1 = createMockWeddingParticipant({
      uuid: "p-1",
      client_name: "Mariana Rios",
      role: "BRIDE",
      role_display: "Noiva",
      is_primary_signatory: true,
      client_email: "mariana@teste.com",
      client_phone: "11988887777",
    });

    const participant2 = createMockWeddingParticipant({
      uuid: "p-2",
      client_name: "Carlos Alberto Rios",
      role: "FINANCIAL_PAYER",
      role_display: "Contratante Financeiro",
      is_primary_signatory: false,
      client_email: "carlos@teste.com",
    });

    const handleRemove = vi.fn();

    render(
      <WeddingParticipantsSection
        participants={[participant1, participant2]}
        onAddParticipant={vi.fn()}
        onRemoveParticipant={handleRemove}
      />
    );

    expect(screen.getByText("Mariana Rios")).toBeInTheDocument();
    expect(screen.getByText("Noiva")).toBeInTheDocument();
    expect(screen.getByText("Signatário")).toBeInTheDocument();
    expect(screen.getByText("mariana@teste.com")).toBeInTheDocument();

    expect(screen.getByText("Carlos Alberto Rios")).toBeInTheDocument();
    expect(screen.getByText("Contratante Financeiro")).toBeInTheDocument();

    const removeBtn = screen.getByRole("button", {
      name: /remover mariana rios/i,
    });
    fireEvent.click(removeBtn);
    expect(handleRemove).toHaveBeenCalledWith(participant1);
  });
});
