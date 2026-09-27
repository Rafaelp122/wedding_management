import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import ContractsGlobalPage from "@/features/contracts/pages/ContractsGlobalPage";
import {
  createMockContract,
  createMockSupplier,
  createMockWedding,
} from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("ContractsGlobalPage", () => {
  const wedding1 = createMockWedding({
    uuid: "w-1",
    groom_name: "Gabriel",
    bride_name: "Beatriz",
  });

  const supplier1 = createMockSupplier({
    uuid: "s-1",
    name: "Buffet Imperial",
  });

  const contract1 = createMockContract({
    uuid: "c-1",
    wedding: "w-1",
    supplier: "s-1",
    supplier_name: "Buffet Imperial",
    name: "Buffet Completo",
    base_amount: "10000.00",
    total_amount: "10000.00",
    addendums_count: 1,
    addendums_total: "2000.00",
    addendums_total_amount: "2000.00",
    effective_amount: "12000.00",
    total_amount_with_addendums: "12000.00",
    status: "SIGNED",
  });

  const contract2 = createMockContract({
    uuid: "c-2",
    wedding: "w-1",
    supplier: "s-1",
    supplier_name: "Buffet Imperial",
    name: "Decoração Floral",
    base_amount: "5000.00",
    total_amount: "5000.00",
    addendums_count: 0,
    addendums_total: "0.00",
    effective_amount: "5000.00",
    status: "PENDING",
  });

  beforeEach(() => {
    vi.clearAllMocks();

    server.use(
      http.get("*/api/v1/contracts/", () => {
        return HttpResponse.json({
          items: [contract1, contract2],
          count: 2,
        });
      }),
      http.get("*/api/v1/suppliers/", () => {
        return HttpResponse.json({
          items: [supplier1],
          count: 1,
        });
      }),
      http.get("*/api/v1/weddings/", () => {
        return HttpResponse.json({
          items: [wedding1],
          count: 1,
        });
      }),
    );
  });

  it("renderiza o cabeçalho e métricas rápidas", async () => {
    render(<ContractsGlobalPage />);

    expect(await screen.findByRole("heading", { name: "Contratos" })).toBeInTheDocument();
    expect(
      screen.getByText("Gestão centralizada de todos os contratos e termos aditivos da assessoria."),
    ).toBeInTheDocument();

    // Métricas
    expect(screen.getByText("Total de Contratos")).toBeInTheDocument();
    expect(screen.getByText("Formalizados / Assinados")).toBeInTheDocument();
    expect(screen.getByText("Pendentes de Assinatura")).toBeInTheDocument();
  });

  it("renderiza a tabela de contratos com as colunas corporativas e valores do backend", async () => {
    render(<ContractsGlobalPage />);

    // Casamento identificado
    const weddingCells = await screen.findAllByText(/Gabriel & Beatriz/);
    expect(weddingCells.length).toBeGreaterThanOrEqual(1);

    // Contratos
    expect(screen.getByText("Buffet Completo")).toBeInTheDocument();
    expect(screen.getByText("Decoração Floral")).toBeInTheDocument();

    // Valores calculados pelo backend
    expect(screen.getByText("R$ 10.000,00")).toBeInTheDocument();
    expect(screen.getByText("+ R$ 2.000,00")).toBeInTheDocument();
    expect(screen.getByText("R$ 12.000,00")).toBeInTheDocument();

    // Badges de status
    expect(screen.getByText("Assinado")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });

  it("filtra contratos via busca textual", async () => {
    const user = userEvent.setup();
    render(<ContractsGlobalPage />);

    expect(await screen.findByText("Buffet Completo")).toBeInTheDocument();
    expect(screen.getByText("Decoração Floral")).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText(/buscar por contrato/i);
    await user.type(searchInput, "Floral");

    expect(screen.queryByText("Buffet Completo")).not.toBeInTheDocument();
    expect(screen.getByText("Decoração Floral")).toBeInTheDocument();
  });

  it("exibe estado vazio quando nenhum contrato coincide com a busca", async () => {
    const user = userEvent.setup();
    render(<ContractsGlobalPage />);

    expect(await screen.findByText("Buffet Completo")).toBeInTheDocument();

    const searchInput = screen.getByPlaceholderText(/buscar por contrato/i);
    await user.type(searchInput, "Inexistente");

    expect(screen.getByText("Nenhum contrato encontrado")).toBeInTheDocument();
  });

  it("abre o diálogo de detalhes ao clicar no botão Detalhes", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/contracts/:uuid/details/", () => {
        return HttpResponse.json({
          contract: contract1,
          items: [],
          addendums: [],
        });
      }),
    );

    render(<ContractsGlobalPage />);

    const detailButtons = await screen.findAllByRole("button", {
      name: /detalhes/i,
    });
    expect(detailButtons.length).toBeGreaterThanOrEqual(1);

    await user.click(detailButtons[0]);

    // O modal deve ser exibido com os dados do contrato selecionado
    expect(await screen.findByRole("dialog")).toBeInTheDocument();
  });

  it("exibe mensagem de erro quando o carregamento de contratos falha", async () => {
    server.use(
      http.get("*/api/v1/contracts/", () => {
        return HttpResponse.json(
          { detail: "Falha de conexão com o banco de dados." },
          { status: 500 },
        );
      }),
    );

    render(<ContractsGlobalPage />);

    expect(
      await screen.findByText("Falha de conexão com o banco de dados."),
    ).toBeInTheDocument();
  });
});
