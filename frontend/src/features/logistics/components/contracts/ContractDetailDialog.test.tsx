import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { ContractDetailDialog } from "./ContractDetailDialog";
import { createMockContract } from "@/test-data";

// ---------------------------------------------------------------------------
// Mock state for logistics hooks – vi.hoisted is used so the values are
// available at module scope before the vi.mock factory runs.
// ---------------------------------------------------------------------------
const mockReadState = vi.hoisted(() => ({
  isLoading: false,
  data: undefined as { data: ReturnType<typeof createMockContract> } | undefined,
}));

const mockItemsState = vi.hoisted(() => ({
  isLoading: false,
  data: { data: { items: [] as Array<Record<string, unknown>>, count: 0 } },
}));

const mockContractsListState = vi.hoisted(() => ({
  data: { data: { items: [] as unknown[], count: 0 } },
}));

vi.mock(
  "@/api/generated/v1/endpoints/logistics/logistics",
  async () => {
    return {
      useLogisticsContractsRead: () => ({
        data: mockReadState.data,
        isLoading: mockReadState.isLoading,
      }),
      useLogisticsItemsList: () => ({
        data: mockItemsState.data,
        isLoading: mockItemsState.isLoading,
      }),
      useLogisticsContractsList: () => ({
        data: mockContractsListState.data,
      }),
    };
  },
);

// ---------------------------------------------------------------------------
// Sub-component mocks – they have their own test suites.
// ---------------------------------------------------------------------------
vi.mock("./ContractDocumentSection", () => ({
  ContractDocumentSection: () => null,
}));
vi.mock("./ContractItemsSection", () => ({
  ContractItemsSection: () => null,
}));

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const WEDDING_UUID = "w-1";
const CONTRACT_UUID = "c-1";

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

// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
// Tests
// ---------------------------------------------------------------------------
describe("ContractDetailDialog", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockReadState.isLoading = false;
    mockReadState.data = undefined;
    mockItemsState.isLoading = false;
    mockItemsState.data = { data: { items: [], count: 0 } };
    mockContractsListState.data = { data: { items: [], count: 0 } };
  });

  // -----------------------------------------------------------------------
  // 1. Loading state
  // -----------------------------------------------------------------------
  it("shows loading skeleton while contract is loading", () => {
    mockReadState.isLoading = true;

    renderDialog();

    // No data message nor not-found should be rendered
    expect(screen.queryByText("Contrato não encontrado")).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Buffet contrato|Valor Total|Fornecedor/),
    ).not.toBeInTheDocument();

    // Skeletons render as divs with "animate-pulse" class
    const skeletons = document.querySelectorAll(".animate-pulse");
    expect(skeletons.length).toBeGreaterThanOrEqual(3);
  });

  // -----------------------------------------------------------------------
  // 2. Not-found state
  // -----------------------------------------------------------------------
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

  // -----------------------------------------------------------------------
  // 3. Basic contract data rendering
  // -----------------------------------------------------------------------
  it("renders contract name, status badge, supplier info, signed date, total amount", () => {
    const contract = createMockContract({
      name: "Buffet Casamento",
      status: "SIGNED",
      supplier_name: "Buffet Ltda",
      signed_date: "2025-01-15",
      total_amount: "5000.00",
      description: "Buffet completo",
    });

    mockReadState.data = { data: contract };

    renderDialog();

    // Title – uses name
    expect(screen.getByText("Buffet Casamento")).toBeInTheDocument();

    // Status badge (SIGNED → "Assinado")
    expect(screen.getByText("Assinado")).toBeInTheDocument();

    // Supplier info
    expect(screen.getByText(/Buffet Ltda/)).toBeInTheDocument();

    // Signed date (formatted pt-BR)
    expect(screen.getByText(/15\/01\/2025/)).toBeInTheDocument();

    // Total amount
    expect(screen.getByText(/R\$\s*5\.000,00/)).toBeInTheDocument();

    // Description
    expect(screen.getByText("Buffet completo")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 4. Supplier clickable
  // -----------------------------------------------------------------------
  it("shows supplier name as clickable button when onSupplierClick is provided", async () => {
    const onSupplierClick = vi.fn();
    const contract = createMockContract({
      supplier: "supplier-uuid-123",
      supplier_name: "Buffet Ltda",
    });

    mockReadState.data = { data: contract };

    renderDialog({ onSupplierClick });

    const supplierButton = screen.getByRole("button", {
      name: /Buffet Ltda/i,
    });
    expect(supplierButton).toBeInTheDocument();

    await userEvent.click(supplierButton);
    expect(onSupplierClick).toHaveBeenCalledWith("supplier-uuid-123");
  });

  // -----------------------------------------------------------------------
  // 5. WhatsApp and Mail links
  // -----------------------------------------------------------------------
  it("shows WhatsApp and Mail links when supplier_phone and supplier_email are present", () => {
    const contract = createMockContract({
      supplier_name: "Fornecedor Teste",
      supplier_phone: "(11) 99999-0000",
      supplier_email: "contato@fornecedor.com",
    });

    mockReadState.data = { data: contract };

    renderDialog();

    // WhatsApp link — the anchor only contains an SVG icon with no accessible
    // name, so we query via href attribute on document.body (Radix portals
    // the dialog content outside the RTL container).
    const waAnchor = document.querySelector(
      'a[href*="wa.me"]',
    ) as HTMLAnchorElement;
    expect(waAnchor).not.toBeNull();
    expect(waAnchor!.href).toContain("wa.me/5511999990000");

    // Mail link
    const mailAnchor = document.querySelector(
      'a[href^="mailto:"]',
    ) as HTMLAnchorElement;
    expect(mailAnchor).not.toBeNull();
    expect(mailAnchor!.href).toBe("mailto:contato@fornecedor.com");
  });

  // -----------------------------------------------------------------------
  // 6. Expense section with progress
  // -----------------------------------------------------------------------
  it("shows expense section with progress when has_linked_expense is true", () => {
    const contract = createMockContract({
      has_linked_expense: true,
      total_amount: "8000.00",
      progress_percent: 60,
      expense_uuid: "exp-1",
    });

    mockReadState.data = { data: contract };

    renderDialog();

    // Section title
    expect(screen.getByText("Despesa Vinculada")).toBeInTheDocument();

    // Progress percent text
    expect(screen.getByText("60% pago")).toBeInTheDocument();

    // Total amount is rendered twice (header + expense section), so use getAll
    const amounts = screen.getAllByText(/R\$\s*8\.000,00/);
    expect(amounts.length).toBeGreaterThanOrEqual(2);

    // Progress bar
    expect(screen.getByRole("progressbar")).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 7. "Ver detalhes da despesa →" button
  // -----------------------------------------------------------------------
  it('shows "Ver detalhes da despesa →" button and calls onExpenseClick', async () => {
    const onExpenseClick = vi.fn();
    const contract = createMockContract({
      has_linked_expense: true,
      expense_uuid: "exp-1",
      total_amount: "5000.00",
    });

    mockReadState.data = { data: contract };

    renderDialog({ onExpenseClick });

    const detailBtn = screen.getByRole("button", {
      name: /ver detalhes da despesa/i,
    });
    expect(detailBtn).toBeInTheDocument();

    await userEvent.click(detailBtn);
    expect(onExpenseClick).toHaveBeenCalledWith("exp-1");
  });

  // -----------------------------------------------------------------------
  // 8. No linked expense
  // -----------------------------------------------------------------------
  it('shows "Nenhuma despesa vinculada" when has_linked_expense is false', () => {
    const contract = createMockContract({
      has_linked_expense: false,
    });

    mockReadState.data = { data: contract };

    renderDialog();

    expect(
      screen.getByText("Nenhuma despesa vinculada a este contrato."),
    ).toBeInTheDocument();

    // No "Gerar Despesa" button since onGenerateExpense is not provided
    expect(
      screen.queryByRole("button", { name: /gerar despesa/i }),
    ).not.toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 9. "Gerar Despesa" button
  // -----------------------------------------------------------------------
  it('shows "Gerar Despesa" button when onGenerateExpense is provided', async () => {
    const onGenerateExpense = vi.fn();
    const contract = createMockContract({
      has_linked_expense: false,
    });

    mockReadState.data = { data: contract };

    renderDialog({ onGenerateExpense });

    const generateBtn = screen.getByRole("button", {
      name: /gerar despesa/i,
    });
    expect(generateBtn).toBeInTheDocument();

    await userEvent.click(generateBtn);
    expect(onGenerateExpense).toHaveBeenCalledWith(contract);
  });

  // -----------------------------------------------------------------------
  // 10. Addendums table
  // -----------------------------------------------------------------------
  it("shows addendums table when addendums exist", () => {
    const contract = createMockContract();

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

    mockReadState.data = { data: contract };
    mockContractsListState.data = {
      data: { items: [addendum1, addendum2], count: 2 },
    };

    renderDialog();

    // Section title
    expect(screen.getByText("Aditivos")).toBeInTheDocument();

    // Addendum names
    expect(screen.getByText("Aditivo Prazo")).toBeInTheDocument();
    expect(screen.getByText("Aditivo Escopo")).toBeInTheDocument();

    // Addendum amounts
    expect(screen.getByText(/1\.000,00/)).toBeInTheDocument();
    expect(screen.getByText(/2\.500,00/)).toBeInTheDocument();

    // Addendum statuses
    expect(screen.getByText("Assinado")).toBeInTheDocument(); // SIGNED
    expect(screen.getByText("Rascunho")).toBeInTheDocument(); // DRAFT
  });

  // -----------------------------------------------------------------------
  // 11. "Criar Aditivo" button
  // -----------------------------------------------------------------------
  it('shows "Criar Aditivo" button when onCreateAddendum is provided', async () => {
    const onCreateAddendum = vi.fn();
    const contract = createMockContract();

    mockReadState.data = { data: contract };

    renderDialog({ onCreateAddendum });

    const addendumBtn = screen.getByRole("button", {
      name: /criar aditivo/i,
    });
    expect(addendumBtn).toBeInTheDocument();

    await userEvent.click(addendumBtn);
    expect(onCreateAddendum).toHaveBeenCalledWith(CONTRACT_UUID);
  });
});
