
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractDetailDialog } from "./ContractDetailDialog";
import { createMockContract } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse, delay } from "msw";

/* Seções filhas são stub — não precisam ser testadas aqui */
vi.mock("./ContractDocumentSection", () => ({
  ContractDocumentSection: () => null,
}));
vi.mock("./ContractItemsSection", () => ({
  ContractItemsSection: () => null,
}));

const WEDDING_UUID = "w-1";
const CONTRACT_UUID = "c-1";

const DEFAULT_CONTRACT = createMockContract();

function renderDialog(
  props: Partial<React.ComponentProps<typeof ContractDetailDialog>> = {},
) {
  return render(
    <ContractDetailDialog
      contractUuid={CONTRACT_UUID}
      weddingUuid={WEDDING_UUID}
      open={true}
      onOpenChange={vi.fn()}
      {...props}
    />,
  );
}

describe("ContractDetailDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(DEFAULT_CONTRACT);
      }),
      http.get("*/api/v1/logistics/items/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      })
    );
  });

  /* ─────────────── Loading ─────────────── */

  it("shows loading skeleton while contract is loading", () => {
    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", async () => {
        await delay("infinite");
        return HttpResponse.json(DEFAULT_CONTRACT);
      }),
    );

    renderDialog();

    expect(
      screen.queryByText("Contrato não encontrado"),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Buffet contrato|Valor Total|Fornecedor/),
    ).not.toBeInTheDocument();

    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(3);
  });

  /* ─────────────── Contracto não encontrado ─────────────── */

  it('shows "Contrato não encontrado" when contractUuid is null', () => {
    renderDialog({ contractUuid: null });

    expect(
      screen.getByText("Contrato não encontrado"),
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        "Os dados deste contrato não estão disponíveis.",
      ),
    ).toBeInTheDocument();
  });

  /* ─────────────── Renderização de dados ─────────────── */
  it("renders contract name, status badge, supplier info, signed date, total amount", async () => {
    const contract = createMockContract({
      name: "Buffet Casamento",
      status: "SIGNED",
      supplier_name: "Buffet Ltda",
      signed_date: "2025-01-15",
      total_amount: "5000.00",
      description: "Buffet completo",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog();

    expect(await screen.findByText("Buffet Casamento")).toBeInTheDocument();
    expect(screen.getByText("Assinado")).toBeInTheDocument();
    expect(screen.getByText(/Buffet Ltda/)).toBeInTheDocument();
    expect(screen.getByText(/15\/01\/2025/)).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*5\.000,00/)).toBeInTheDocument();
    expect(screen.getByText("Buffet completo")).toBeInTheDocument();
  });

  it("shows supplier name as clickable button when onSupplierClick is provided", async () => {
    const onSupplierClick = vi.fn();
    const contract = createMockContract({
      supplier: "supplier-uuid-123",
      supplier_name: "Buffet Ltda",
    });
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog({ onSupplierClick });

    const supplierButton = await screen.findByRole("button", {
      name: /Buffet Ltda/i,
    });
    expect(supplierButton).toBeInTheDocument();

    await user.click(supplierButton);
    expect(onSupplierClick).toHaveBeenCalledWith("supplier-uuid-123");
  });

  it("shows WhatsApp and Mail links when supplier_phone and supplier_email are present", async () => {
    const contract = createMockContract({
      supplier_name: "Fornecedor Teste",
      supplier_phone: "(11) 99999-0000",
      supplier_email: "contato@fornecedor.com",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog();

    // Aguarda carregar
    await screen.findByText("Fornecedor Teste");

    /* wa.me com dígitos limpos */
    const waAnchor = document.querySelector(
      'a[href*="wa.me"]',
    ) as HTMLAnchorElement;
    expect(waAnchor).not.toBeNull();
    expect(waAnchor!.href).toContain("wa.me/5511999990000");

    const mailAnchor = document.querySelector(
      'a[href^="mailto:"]',
    ) as HTMLAnchorElement;
    expect(mailAnchor).not.toBeNull();
    expect(mailAnchor!.href).toBe("mailto:contato@fornecedor.com");
  });

  /* ─────────────── Despesa Vinculada ─────────────── */

  it("shows expense section with progress when has_linked_expense is true", async () => {
    const contract = createMockContract({
      has_linked_expense: true,
      total_amount: "8000.00",
      progress_percent: 60,
      expense_uuid: "exp-1",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog();

    expect(await screen.findByText("Despesa Vinculada")).toBeInTheDocument();
    expect(screen.getByText("60% pago")).toBeInTheDocument();

    const amounts = screen.getAllByText(/R\$\s*8\.000,00/);
    expect(amounts.length).toBeGreaterThanOrEqual(2);

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  it('shows "Ver detalhes da despesa →" button and calls onExpenseClick', async () => {
    const onExpenseClick = vi.fn();
    const contract = createMockContract({
      has_linked_expense: true,
      expense_uuid: "exp-1",
      total_amount: "5000.00",
    });
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog({ onExpenseClick });

    const detailBtn = await screen.findByRole("button", {
      name: /ver detalhes da despesa/i,
    });
    expect(detailBtn).toBeInTheDocument();

    await user.click(detailBtn);
    expect(onExpenseClick).toHaveBeenCalledWith("exp-1");
  });

  it('shows "Nenhuma despesa vinculada" when has_linked_expense is false', async () => {
    const contract = createMockContract({
      has_linked_expense: false,
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog();

    expect(
      await screen.findByText("Nenhuma despesa vinculada a este contrato."),
    ).toBeInTheDocument();

    expect(
      screen.queryByRole("button", { name: /gerar despesa/i }),
    ).not.toBeInTheDocument();
  });

  it('shows "Gerar Despesa" button when onGenerateExpense is provided', async () => {
    const onGenerateExpense = vi.fn();
    const contract = createMockContract({
      has_linked_expense: false,
    });
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contract);
      })
    );

    renderDialog({ onGenerateExpense });

    const generateBtn = await screen.findByRole("button", {
      name: /gerar despesa/i,
    });
    expect(generateBtn).toBeInTheDocument();

    await user.click(generateBtn);
    expect(onGenerateExpense).toHaveBeenCalledWith(contract);
  });

  /* ─────────────── Aditivos ─────────────── */

  it("shows addendums table when addendums exist", async () => {
    const addendum1 = createMockContract({
      uuid: "addendum-1",
      name: "Aditivo Prazo",
      total_amount: "1000.00",
      status: "SIGNED",
      parent: CONTRACT_UUID,
    });
    const addendum2 = createMockContract({
      uuid: "addendum-2",
      name: "Aditivo Escopo",
      total_amount: "2500.00",
      status: "DRAFT",
      parent: CONTRACT_UUID,
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [addendum1, addendum2], count: 2 });
      })
    );

    renderDialog();

    expect(await screen.findByText("Aditivos")).toBeInTheDocument();
    expect(screen.getByText("Aditivo Prazo")).toBeInTheDocument();
    expect(screen.getByText("Aditivo Escopo")).toBeInTheDocument();
    expect(screen.getAllByText(/1\.000,00/).length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText(/2\.500,00/).length).toBeGreaterThanOrEqual(1);

    // Verifica exibição do resumo financeiro consolidado
    expect(screen.getByText("Valor Principal:")).toBeInTheDocument();
    expect(screen.getByText("Total Consolidado:")).toBeInTheDocument();
    expect(screen.getByText("Total dos Aditivos")).toBeInTheDocument();

    const assinadoBadges = screen.getAllByText("Assinado");
    expect(assinadoBadges.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Rascunho")).toBeInTheDocument();
  });

  it("shows consolidated total from API fields when provided", async () => {
    const contractWithAddendums = createMockContract({
      total_amount: "10000.00",
      addendums_count: 2,
      addendums_total_amount: "3500.00",
      total_amount_with_addendums: "13500.00",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(contractWithAddendums);
      })
    );

    renderDialog();

    expect(await screen.findByText("Valor Principal:")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*10\.000,00/)).toBeInTheDocument();
    expect(screen.getByText("Aditivos (2):")).toBeInTheDocument();
    expect(screen.getByText(/\+\s*R\$\s*3\.500,00/)).toBeInTheDocument();
    expect(screen.getByText("Total Consolidado:")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*13\.500,00/)).toBeInTheDocument();
  });

  it("ignores canceled addendums when calculating fallback sum without API fields", async () => {
    const mainContract = createMockContract({
      total_amount: "5000.00",
      addendums_count: 0,
      addendums_total_amount: undefined,
      total_amount_with_addendums: undefined,
    });
    const activeAddendum = createMockContract({
      uuid: "ad-1",
      name: "Aditivo Ativo",
      total_amount: "2000.00",
      status: "SIGNED",
      parent: CONTRACT_UUID,
    });
    const canceledAddendum = createMockContract({
      uuid: "ad-2",
      name: "Aditivo Cancelado",
      total_amount: "3000.00",
      status: "CANCELED",
      parent: CONTRACT_UUID,
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(mainContract);
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({
          items: [activeAddendum, canceledAddendum],
          count: 2,
        });
      })
    );

    renderDialog();

    expect(await screen.findByText("Valor Principal:")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*5\.000,00/)).toBeInTheDocument();
    // Apenas o aditivo ativo de 2000 é somado
    expect(screen.getByText(/\+\s*R\$\s*2\.000,00/)).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*7\.000,00/)).toBeInTheDocument();
  });

  it("renders simple 'Valor Total' when contract has no addendums", async () => {
    const simpleContract = createMockContract({
      total_amount: "8000.00",
      addendums_count: 0,
      addendums_total_amount: "0.00",
      total_amount_with_addendums: "8000.00",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/", () => {
        return HttpResponse.json(simpleContract);
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      })
    );

    renderDialog();

    expect(await screen.findByText("Valor Total:")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*8\.000,00/)).toBeInTheDocument();
    expect(screen.queryByText("Valor Principal:")).not.toBeInTheDocument();
    expect(screen.queryByText("Total Consolidado:")).not.toBeInTheDocument();
  });

  it('shows "Criar Aditivo" button when onCreateAddendum is provided', async () => {
    const onCreateAddendum = vi.fn();
    const user = userEvent.setup();

    renderDialog({ onCreateAddendum });

    const addendumBtn = await screen.findByRole("button", {
      name: /criar aditivo/i,
    });
    expect(addendumBtn).toBeInTheDocument();

    await user.click(addendumBtn);
    expect(onCreateAddendum).toHaveBeenCalledWith(CONTRACT_UUID);
  });
});
