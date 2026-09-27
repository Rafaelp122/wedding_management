import { describe, it, expect, vi } from "vitest";
import { render, screen } from "@/test-utils";
import { AddParticipantDialog } from "./AddParticipantDialog";

describe("AddParticipantDialog (Smart Component)", () => {
  it("renderiza campos e abas de seleção de participantes quando aberto", () => {
    const handleOpenChange = vi.fn();

    render(
      <AddParticipantDialog
        weddingUuid="w-1"
        open={true}
        onOpenChange={handleOpenChange}
      />
    );

    expect(
      screen.getByText("Vincular Participante ao Casamento")
    ).toBeInTheDocument();
    expect(screen.getByText("Cliente Existente")).toBeInTheDocument();
    expect(screen.getByText("Novo Contato / Cliente")).toBeInTheDocument();
  });
});
