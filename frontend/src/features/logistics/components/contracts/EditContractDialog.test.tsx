import { beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { EditContractDialog } from "./EditContractDialog";
import { createMockContract, createMockSupplier } from "@/test-data";

// Polyfills for Radix UI Select in jsdom (missing browser APIs)
beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

// ============================================================================
// Hoisted mocks – available at module scope before vi.mock factories run
// ============================================================================

const { toastSuccess, toastError } = vi.hoisted(() => ({
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
}));

vi.mock("sonner", async (importOriginal) => {
  const actual = await importOriginal<typeof import("sonner")>();
  return {
    ...actual,
    toast: {
      ...actual.toast,
      success: toastSuccess,
      error: toastError,
    },
  };
});

const mockMutate = vi.hoisted(
  () => vi.fn((_variables, options) => options?.onSuccess?.(null)),
);

const mockSuppliersList = vi.hoisted(() => vi.fn());
const mockContractsList = vi.hoisted(() => vi.fn());

vi.mock(
  "@/api/generated/v1/endpoints/logistics/logistics",
  async () => ({
    useLogisticsContractsUpdate: () => ({
      mutate: mockMutate,
      isPending: false,
    }),
    useLogisticsSuppliersList: () => mockSuppliersList(),
    useLogisticsContractsList: () => mockContractsList(),
  }),
);

// ============================================================================
// Helpers
// ============================================================================

function mockQueryResponse(data: unknown) {
  return { data, isLoading: false, isError: false, error: null };
}

const mockSupplier = createMockSupplier({
  uuid: "supplier-uuid-123",
  name: "Buffet Gourmet Ltda",
});

const weddingUuid = "test-wedding-uuid";

function createMockContractWithName(overrides: Partial<Record<string, unknown>> = {}) {
  return createMockContract({
    uuid: "contract-1",
    name: "Buffet Casamento",
    supplier: "supplier-uuid-123",
    total_amount: "5000.00",
    status: "SIGNED",
    description: "Buffet para 150 convidados",
    ...overrides,
  });
}

// ============================================================================
// Tests
// ============================================================================

describe("EditContractDialog", () => {
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [mockSupplier], count: 1 } }),
    );
    mockContractsList.mockReturnValue(
      mockQueryResponse({ data: { items: [], count: 0 } }),
    );
  });

  // -----------------------------------------------------------------------
  // 1. Renders form with pre-filled data
  // -----------------------------------------------------------------------
  it("renders form with pre-filled data", () => {
    const contract = createMockContractWithName();

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // Dialog title and description
    expect(screen.getByText("Editar Contrato")).toBeInTheDocument();
    expect(
      screen.getByText("Altere os metadados do contrato de fornecedor."),
    ).toBeInTheDocument();

    // Pre-filled name input
    expect(screen.getByLabelText("Nome do Contrato")).toHaveValue(
      "Buffet Casamento",
    );

    // Pre-filled description
    expect(screen.getByLabelText("Descrição")).toHaveValue(
      "Buffet para 150 convidados",
    );

    // Pre-filled total_amount (number input)
    const amountInput = screen.getByRole("spinbutton", {
      name: /valor total/i,
    });
    expect(amountInput).toHaveValue(5000);

    // Selects rendered
    expect(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();

    // Submit button
    expect(
      screen.getByRole("button", { name: /salvar/i }),
    ).toBeInTheDocument();
  });

  // -----------------------------------------------------------------------
  // 2. Submits only changed fields
  // -----------------------------------------------------------------------
  it("submits only changed fields", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // Change the name field
    const nameInput = screen.getByLabelText("Nome do Contrato");
    await user.clear(nameInput);
    await user.type(nameInput, "Buffet VIP Atualizado");

    // Submit
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(mockMutate).toHaveBeenCalledWith(
        { uuid: "contract-1", data: { name: "Buffet VIP Atualizado" } },
        expect.any(Object),
      );
    });
  });

  // -----------------------------------------------------------------------
  // 3. Ignores submit when nothing changed
  // -----------------------------------------------------------------------
  it("ignores submit when nothing changed", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // Click submit without making any changes
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    // mutate should NOT have been called
    expect(mockMutate).not.toHaveBeenCalled();

    // Dialog should have been closed via the empty-payload guard
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  // -----------------------------------------------------------------------
  // 4. Shows success toast on successful submit
  // -----------------------------------------------------------------------
  it("shows success toast on successful submit", async () => {
    const user = userEvent.setup();
    const contract = createMockContractWithName();

    render(
      <EditContractDialog
        contract={contract}
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // Change the name
    const nameInput = screen.getByLabelText("Nome do Contrato");
    await user.clear(nameInput);
    await user.type(nameInput, "Nome Alterado");

    // Submit
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith(
        "Contrato atualizado com sucesso!",
      );
    });

    // onSuccess callback from props should have been called
    expect(onSuccess).toHaveBeenCalled();
  });
});
