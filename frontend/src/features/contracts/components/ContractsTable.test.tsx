import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractsTable } from "./ContractsTable";
import { createMockContract } from "@/test-data";

describe("ContractsTable", () => {
  it("exibe mensagem vazia quando não há contratos", () => {
    render(<ContractsTable contracts={[]} />);

    expect(
      screen.getByText("Nenhum contrato encontrado com os filtros aplicados."),
    ).toBeInTheDocument();
  });

  it("renderiza linhas da tabela com colunas corporativas e valores formatados", () => {
    const contract = createMockContract({
      uuid: "c-1",
      wedding: "wedding-uuid-1",
      supplier_name: "Fornecedor Premier",
      name: "Serviço de Buffet",
      base_amount: "8000.00",
      total_amount: "8000.00",
      addendums_total: "1500.00",
      addendums_total_amount: "1500.00",
      effective_amount: "9500.00",
      total_amount_with_addendums: "9500.00",
      status: "SIGNED",
    });

    render(
      <ContractsTable
        contracts={[contract]}
        weddingMap={{ "wedding-uuid-1": "Lucas & Juliana" }}
      />,
    );

    expect(screen.getByText("Lucas & Juliana")).toBeInTheDocument();
    expect(screen.getByText("Fornecedor Premier")).toBeInTheDocument();
    expect(screen.getByText("Serviço de Buffet")).toBeInTheDocument();
    expect(screen.getByText("R$ 8.000,00")).toBeInTheDocument();
    expect(screen.getByText("+ R$ 1.500,00")).toBeInTheDocument();
    expect(screen.getByText("R$ 9.500,00")).toBeInTheDocument();
    expect(screen.getByText("Assinado")).toBeInTheDocument();
  });

  it("chama onViewDetails ao clicar no botão Detalhes", async () => {
    const user = userEvent.setup();
    const onViewDetails = vi.fn();
    const contract = createMockContract({
      uuid: "c-2",
      name: "Fotografia",
    });

    render(
      <ContractsTable
        contracts={[contract]}
        onViewDetails={onViewDetails}
      />,
    );

    const detailsButton = screen.getByRole("button", { name: /detalhes/i });
    expect(detailsButton).toBeInTheDocument();

    await user.click(detailsButton);
    expect(onViewDetails).toHaveBeenCalledTimes(1);
    expect(onViewDetails).toHaveBeenCalledWith(contract);
  });
});
