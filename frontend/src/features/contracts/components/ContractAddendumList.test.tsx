import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractAddendumList } from "./ContractAddendumList";
import { createMockContractAddendum } from "@/test-data";

describe("ContractAddendumList", () => {
  it("exibe mensagem vazia quando não há aditivos", () => {
    render(<ContractAddendumList addendums={[]} />);

    expect(
      screen.getByText("Nenhum aditivo registrado para este contrato."),
    ).toBeInTheDocument();
  });

  it("renderiza lista de aditivos com valores, datas, justificativas e status", () => {
    const addendum1 = createMockContractAddendum({
      uuid: "ad-1",
      amount: "1500.00",
      justification: "Inclusão de hora extra",
      status: "PENDING",
      signed_date: "2025-02-10",
    });
    const addendum2 = createMockContractAddendum({
      uuid: "ad-2",
      amount: "2800.50",
      justification: "Acréscimo de convidados",
      status: "SIGNED",
      signed_date: "2025-02-15",
    });

    render(<ContractAddendumList addendums={[addendum1, addendum2]} />);

    expect(screen.getByText("Inclusão de hora extra")).toBeInTheDocument();
    expect(screen.getByText("Acréscimo de convidados")).toBeInTheDocument();
    expect(screen.getByText(/1\.500,00/)).toBeInTheDocument();
    expect(screen.getByText(/2\.800,50/)).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
    expect(screen.getByText("Assinado")).toBeInTheDocument();
    expect(screen.getByText("10/02/2025")).toBeInTheDocument();
    expect(screen.getByText("15/02/2025")).toBeInTheDocument();
  });

  it("chama callback onSignAddendum quando botão de assinar é clicado", async () => {
    const user = userEvent.setup();
    const onSignAddendum = vi.fn();
    const addendum = createMockContractAddendum({
      uuid: "ad-pending",
      status: "PENDING",
      amount: "500.00",
    });

    render(
      <ContractAddendumList
        addendums={[addendum]}
        onSignAddendum={onSignAddendum}
      />,
    );

    const signButton = screen.getByRole("button", { name: /assinar/i });
    expect(signButton).toBeInTheDocument();

    await user.click(signButton);
    expect(onSignAddendum).toHaveBeenCalledTimes(1);
    expect(onSignAddendum).toHaveBeenCalledWith(addendum);
  });

  it("não exibe botão de assinar para aditivos já assinados", () => {
    const onSignAddendum = vi.fn();
    const addendum = createMockContractAddendum({
      uuid: "ad-signed",
      status: "SIGNED",
      amount: "500.00",
    });

    render(
      <ContractAddendumList
        addendums={[addendum]}
        onSignAddendum={onSignAddendum}
      />,
    );

    expect(screen.queryByRole("button", { name: /assinar/i })).not.toBeInTheDocument();
  });

  it("filtra aditivos por status e exibe subtotal do filtro", async () => {
    const user = userEvent.setup();
    const pending = createMockContractAddendum({
      uuid: "ad-p",
      amount: "1000.00",
      justification: "Hora extra",
      status: "PENDING",
    });
    const signed = createMockContractAddendum({
      uuid: "ad-s",
      amount: "2500.00",
      justification: "Buffet extra",
      status: "SIGNED",
    });

    render(<ContractAddendumList addendums={[pending, signed]} />);

    expect(screen.getByText("Hora extra")).toBeInTheDocument();
    expect(screen.getByText("Buffet extra")).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: /pendentes/i }));

    expect(screen.getByText("Hora extra")).toBeInTheDocument();
    expect(screen.queryByText("Buffet extra")).not.toBeInTheDocument();
    expect(screen.getByTestId("addendum-subtotal")).toHaveTextContent(/1\.000,00/);

    await user.click(screen.getByRole("button", { name: /assinados/i }));

    expect(screen.queryByText("Hora extra")).not.toBeInTheDocument();
    expect(screen.getByText("Buffet extra")).toBeInTheDocument();
    expect(screen.getByTestId("addendum-subtotal")).toHaveTextContent(/2\.500,00/);
  });

  it("exibe mensagem vazia do filtro quando nenhum aditivo tem o status", async () => {
    const user = userEvent.setup();
    const pending = createMockContractAddendum({
      uuid: "ad-p",
      amount: "1000.00",
      status: "PENDING",
    });

    render(<ContractAddendumList addendums={[pending]} />);

    await user.click(screen.getByRole("button", { name: /cancelados/i }));

    expect(screen.getByText("Nenhum aditivo com este status.")).toBeInTheDocument();
  });

  it("chama callback onCreateAddendum quando botão de novo aditivo é clicado", async () => {
    const user = userEvent.setup();
    const onCreateAddendum = vi.fn();

    render(
      <ContractAddendumList
        addendums={[]}
        onCreateAddendum={onCreateAddendum}
      />,
    );

    const createButton = screen.getByRole("button", { name: /criar aditivo/i });
    expect(createButton).toBeInTheDocument();

    await user.click(createButton);
    expect(onCreateAddendum).toHaveBeenCalledTimes(1);
  });
});
