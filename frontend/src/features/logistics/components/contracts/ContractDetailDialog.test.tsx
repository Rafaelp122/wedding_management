/* eslint-disable @typescript-eslint/no-explicit-any */
import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractDetailDialog } from "./ContractDetailDialog";
import { createMockContract } from "@/test-data";
import {
  useLogisticsContractsRead,
  useLogisticsItemsList,
  useLogisticsContractsList,
} from "@/api/generated/v1/endpoints/logistics/logistics";

/**
 * Mock do módulo Orval logistics para controlar os hooks de contrato.
 * Usamos importOriginal para preservar as demais exports (mutações, etc.)
 * e substituímos apenas os hooks de leitura por vi.fn().
 *
 * Cada teste (ou beforeEach) define o retorno via mockReturnValue.
 */
vi.mock(
  "@/api/generated/v1/endpoints/logistics/logistics",
  async (importOriginal) => {
    const original = await importOriginal<
      typeof import("@/api/generated/v1/endpoints/logistics/logistics")
    >();
    return {
      ...original,
      useLogisticsContractsRead: vi.fn(),
      useLogisticsItemsList: vi.fn(),
      useLogisticsContractsList: vi.fn(),
    };
  },
);

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

    /* --- Configuração padrão dos mocks ---
     * Por padrão, o contrato é carregado com sucesso, sem itens e sem aditivos.
     * Cada teste pode sobrescrever com novos mockReturnValue. */
    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: DEFAULT_CONTRACT },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    vi.mocked(useLogisticsItemsList).mockReturnValue({
      data: { data: { items: [], count: 0 } },
      isLoading: false,
    } as any);

    vi.mocked(useLogisticsContractsList).mockReturnValue({
      data: { data: { items: [], count: 0 } },
      isLoading: false,
    } as any);
  });

  /* ─────────────── Loading ─────────────── */

  it("shows loading skeleton while contract is loading", () => {
    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as any);

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
    /* Quando contractUuid é null o hook não é executado (enabled: false),
     * então o retorno do mock não importa — o data fica undefined. */
    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

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

  it("renders contract name, status badge, supplier info, signed date, total amount", () => {
    const contract = createMockContract({
      name: "Buffet Casamento",
      status: "SIGNED",
      supplier_name: "Buffet Ltda",
      signed_date: "2025-01-15",
      total_amount: "5000.00",
      description: "Buffet completo",
    });

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog();

    expect(screen.getByText("Buffet Casamento")).toBeInTheDocument();
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

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog({ onSupplierClick });

    const supplierButton = screen.getByRole("button", {
      name: /Buffet Ltda/i,
    });
    expect(supplierButton).toBeInTheDocument();

    await user.click(supplierButton);
    expect(onSupplierClick).toHaveBeenCalledWith("supplier-uuid-123");
  });

  it("shows WhatsApp and Mail links when supplier_phone and supplier_email are present", () => {
    const contract = createMockContract({
      supplier_name: "Fornecedor Teste",
      supplier_phone: "(11) 99999-0000",
      supplier_email: "contato@fornecedor.com",
    });

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog();

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

  it("shows expense section with progress when has_linked_expense is true", () => {
    const contract = createMockContract({
      has_linked_expense: true,
      total_amount: "8000.00",
      progress_percent: 60,
      expense_uuid: "exp-1",
    });

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog();

    expect(screen.getByText("Despesa Vinculada")).toBeInTheDocument();
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

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog({ onExpenseClick });

    const detailBtn = screen.getByRole("button", {
      name: /ver detalhes da despesa/i,
    });
    expect(detailBtn).toBeInTheDocument();

    await user.click(detailBtn);
    expect(onExpenseClick).toHaveBeenCalledWith("exp-1");
  });

  it('shows "Nenhuma despesa vinculada" when has_linked_expense is false', () => {
    const contract = createMockContract({
      has_linked_expense: false,
    });

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog();

    expect(
      screen.getByText("Nenhuma despesa vinculada a este contrato."),
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

    vi.mocked(useLogisticsContractsRead).mockReturnValue({
      data: { data: contract },
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderDialog({ onGenerateExpense });

    const generateBtn = screen.getByRole("button", {
      name: /gerar despesa/i,
    });
    expect(generateBtn).toBeInTheDocument();

    await user.click(generateBtn);
    expect(onGenerateExpense).toHaveBeenCalledWith(contract);
  });

  /* ─────────────── Aditivos ─────────────── */

  it("shows addendums table when addendums exist", () => {
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

    vi.mocked(useLogisticsContractsList).mockReturnValue({
      data: { data: { items: [addendum1, addendum2], count: 2 } },
      isLoading: false,
    } as any);

    renderDialog();

    expect(screen.getByText("Aditivos")).toBeInTheDocument();
    expect(screen.getByText("Aditivo Prazo")).toBeInTheDocument();
    expect(screen.getByText("Aditivo Escopo")).toBeInTheDocument();
    expect(screen.getByText(/1\.000,00/)).toBeInTheDocument();
    expect(screen.getByText(/2\.500,00/)).toBeInTheDocument();

    const assinadoBadges = screen.getAllByText("Assinado");
    expect(assinadoBadges.length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("Rascunho")).toBeInTheDocument();
  });

  it('shows "Criar Aditivo" button when onCreateAddendum is provided', async () => {
    const onCreateAddendum = vi.fn();
    const user = userEvent.setup();

    renderDialog({ onCreateAddendum });

    const addendumBtn = screen.getByRole("button", {
      name: /criar aditivo/i,
    });
    expect(addendumBtn).toBeInTheDocument();

    await user.click(addendumBtn);
    expect(onCreateAddendum).toHaveBeenCalledWith(CONTRACT_UUID);
  });
});
