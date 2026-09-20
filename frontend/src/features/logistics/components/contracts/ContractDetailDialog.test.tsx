
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { toast } from "sonner";
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

function mockDetails(contract: any, items: any[] = [], addendums: any[] = []) {
  return HttpResponse.json({ contract, items, addendums });
}

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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(DEFAULT_CONTRACT);
      })
    );
  });

  /* ─────────────── Loading ─────────────── */

  it("shows loading skeleton while contract is loading", () => {
    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", async () => {
        await delay("infinite");
        return mockDetails(DEFAULT_CONTRACT);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contract);
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

    const contractWithAddendums = createMockContract({
      total_amount: "5000.00",
      addendums_count: 2,
      addendums_total_amount: "3500.00",
      total_amount_with_addendums: "8500.00",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contractWithAddendums, [], [addendum1, addendum2]);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(contractWithAddendums);
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

  it("shows consolidated totals from contract fields with active and canceled addendums", async () => {
    const mainContract = createMockContract({
      total_amount: "5000.00",
      addendums_count: 1,
      addendums_total_amount: "2000.00",
      total_amount_with_addendums: "7000.00",
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(mainContract, [], [activeAddendum, canceledAddendum]);
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
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(simpleContract);
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

  it("opens SignContractDialog when clicking Formalizar Assinatura on a PENDING contract", async () => {
    const pendingContract = createMockContract({
      status: "PENDING",
      name: "Contrato Pendente",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(pendingContract);
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const signBtn = await screen.findByRole("button", { name: "Formalizar Assinatura" });
    await user.click(signBtn);

    expect(await screen.findByRole("heading", { name: "Formalizar Assinatura" })).toBeInTheDocument();
  });

  it("opens CancelContractDialog when clicking Distratar / Cancelar on a SIGNED contract", async () => {
    const signedContract = createMockContract({
      status: "SIGNED",
      name: "Contrato Assinado",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(signedContract);
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const cancelBtn = await screen.findByRole("button", { name: "Distratar / Cancelar" });
    await user.click(cancelBtn);

    expect(await screen.findByRole("heading", { name: "Cancelar Contrato" })).toBeInTheDocument();
  });

  it("handles Enviar para Assinatura on a DRAFT contract", async () => {
    const draftContract = createMockContract({
      status: "DRAFT",
      name: "Contrato Rascunho",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(draftContract);
      }),
      http.post("*/api/v1/logistics/contracts/:uuid/send-to-pending/", () => {
        return HttpResponse.json({ ...draftContract, status: "PENDING" });
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const sendBtn = await screen.findByRole("button", { name: "Enviar para Assinatura" });
    await user.click(sendBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato enviado para assinatura!");
    });
  });

  it("shows error toast when Enviar para Assinatura fails", async () => {
    const draftContract = createMockContract({
      status: "DRAFT",
      name: "Contrato Rascunho",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(draftContract);
      }),
      http.post("*/api/v1/logistics/contracts/:uuid/send-to-pending/", () => {
        return HttpResponse.json(
          { detail: "Falha ao enviar contrato." },
          { status: 422 },
        );
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const sendBtn = await screen.findByRole("button", { name: "Enviar para Assinatura" });
    await user.click(sendBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Falha ao enviar contrato.");
    });
  });

  it("handles Devolver para Rascunho on a PENDING contract", async () => {
    const pendingContract = createMockContract({
      status: "PENDING",
      name: "Contrato Pendente",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(pendingContract);
      }),
      http.post("*/api/v1/logistics/contracts/:uuid/revert-to-draft/", () => {
        return HttpResponse.json({ ...pendingContract, status: "DRAFT" });
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const revertBtn = await screen.findByRole("button", { name: "Devolver para Rascunho" });
    await user.click(revertBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato retornado para rascunho!");
    });
  });

  it("shows error toast when Devolver para Rascunho fails", async () => {
    const pendingContract = createMockContract({
      status: "PENDING",
      name: "Contrato Pendente",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(pendingContract);
      }),
      http.post("*/api/v1/logistics/contracts/:uuid/revert-to-draft/", () => {
        return HttpResponse.json(
          { detail: "Falha ao reverter contrato." },
          { status: 422 },
        );
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const revertBtn = await screen.findByRole("button", { name: "Devolver para Rascunho" });
    await user.click(revertBtn);

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Falha ao reverter contrato.");
    });
  });

  it("opens CancelContractDialog when clicking Cancelar Contrato on a DRAFT contract", async () => {
    const draftContract = createMockContract({
      status: "DRAFT",
      name: "Contrato Rascunho Para Cancelar",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(draftContract);
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const cancelBtn = await screen.findByRole("button", { name: "Cancelar Contrato" });
    await user.click(cancelBtn);

    expect(await screen.findByRole("heading", { name: "Cancelar Contrato" })).toBeInTheDocument();
  });

  it("opens CancelContractDialog when clicking Cancelar Contrato on a PENDING contract", async () => {
    const pendingContract = createMockContract({
      status: "PENDING",
      name: "Contrato Pendente Para Cancelar",
    });

    server.use(
      http.get("*/api/v1/logistics/contracts/:uuid/details/", () => {
        return mockDetails(pendingContract);
      }),
    );

    const user = userEvent.setup();
    renderDialog();

    const cancelBtn = await screen.findByRole("button", { name: "Cancelar Contrato" });
    await user.click(cancelBtn);

    expect(await screen.findByRole("heading", { name: "Cancelar Contrato" })).toBeInTheDocument();
  });
});
