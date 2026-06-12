import { beforeEach, describe, expect, it, vi, beforeAll } from "vitest";
import { fireEvent, render, screen, userEvent, waitFor } from "@/test-utils";
import { ContractUploadDialog } from "./ContractUploadDialog";

// Polyfills for Radix UI Select in jsdom (missing browser APIs)
beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

// ===== HOISTED MOCKS =====

// Toast mock
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

// Hook mocks
const {
  mockSuppliersList,
  mockContractsList,
  mockCategoriesList,
  mockCreateFull,
  createFullAsync,
} = vi.hoisted(() => ({
  mockSuppliersList: vi.fn(),
  mockContractsList: vi.fn(),
  mockCategoriesList: vi.fn(),
  mockCreateFull: vi.fn(),
  createFullAsync: vi.fn(),
}));

vi.mock("@/api/generated/v1/endpoints/logistics/logistics", () => ({
  useLogisticsSuppliersList: () => mockSuppliersList(),
  useLogisticsContractsList: () => mockContractsList(),
  useLogisticsContractsCreateFull: () => mockCreateFull(),
}));

vi.mock("@/api/generated/v1/endpoints/finances/finances", () => ({
  useFinancesCategoriesList: () => mockCategoriesList(),
}));

// ===== TEST SUITE =====

describe("ContractUploadDialog", () => {
  const weddingUuid = "wedding-1";
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  const defaultProps = {
    weddingUuid,
    open: true,
    onOpenChange,
    onSuccess,
  };

  function mockQueryResponse(data: unknown) {
    return {
      data,
      isLoading: false,
      isError: false,
      error: null,
    };
  }

  const mockSupplier = {
    uuid: "supplier-1",
    name: "Fornecedor Teste",
    cnpj: "12.345.678/0001-90",
    phone: "(11) 99999-8888",
    email: "forn@test.com",
    is_active: true,
    created_at: "2024-01-01T00:00:00Z",
    updated_at: "2024-01-01T00:00:00Z",
  };

  beforeEach(() => {
    vi.clearAllMocks();

    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [], count: 0 } }),
    );
    mockContractsList.mockReturnValue(
      mockQueryResponse({ data: { items: [], count: 0 } }),
    );
    mockCategoriesList.mockReturnValue(
      mockQueryResponse({ data: { items: [], count: 0 } }),
    );

    createFullAsync.mockReset();
    createFullAsync.mockResolvedValue({ data: { uuid: "contract-1" } });

    mockCreateFull.mockReturnValue({
      mutateAsync: createFullAsync,
      isPending: false,
    });
  });

  // ------------------------------------------------------------------
  // 1. Renders nothing when closed
  // ------------------------------------------------------------------
  it("renders nothing when closed", () => {
    render(<ContractUploadDialog {...defaultProps} open={false} />);

    expect(screen.queryByText("Novo Contrato")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /criar contrato/i }),
    ).not.toBeInTheDocument();
  });

  // ------------------------------------------------------------------
  // 2. Renders form fields when open
  // ------------------------------------------------------------------
  it("renders form fields when open", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(screen.getByText("Novo Contrato")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Vincule um fornecedor a este evento com um novo contrato.",
      ),
    ).toBeInTheDocument();

    // Form field labels
    expect(screen.getByText("Fornecedor")).toBeInTheDocument();
    expect(screen.getByText("Nome do Contrato")).toBeInTheDocument();
    expect(screen.getByText("Valor Total")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Descrição")).toBeInTheDocument();

    // Inputs
    expect(
      screen.getByPlaceholderText("Ex: Buffet Completo"),
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Descreva o objeto do contrato..."),
    ).toBeInTheDocument();

    // Comboboxes
    expect(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();

    // Warning alert
    expect(
      screen.getByText(/este sistema não substitui consultoria jurídica/i),
    ).toBeInTheDocument();

    // Buttons
    expect(
      screen.getByRole("button", { name: /cancelar/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /criar contrato/i }),
    ).toBeInTheDocument();
  });

  // ------------------------------------------------------------------
  // 3. Renders item drafts section
  // ------------------------------------------------------------------
  it("renders item drafts section", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(screen.getByText("Itens (Opcional)")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /adicionar/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("Nenhum item adicionado.")).toBeInTheDocument();
  });

  // ------------------------------------------------------------------
  // 4. Renders expense creation checkbox section
  // ------------------------------------------------------------------
  it("renders expense creation checkbox section", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(
      screen.getByText("Criar despesa a partir deste contrato"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: /criar despesa/i }),
    ).toBeInTheDocument();
  });

  // ------------------------------------------------------------------
  // 5. Fills form and submits (verify contract creation is called)
  // ------------------------------------------------------------------
  it("fills form and submits successfully", async () => {
    const user = userEvent.setup();

    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [mockSupplier], count: 1 } }),
    );

    render(<ContractUploadDialog {...defaultProps} />);

    // -- Select supplier --
    await user.click(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    );
    const supplierOption = await screen.findByRole("option", {
      name: /fornecedor teste/i,
    });
    await user.click(supplierOption);

    // -- Fill name --
    await user.type(
      screen.getByRole("textbox", { name: /nome do contrato/i }),
      "Contrato Teste",
    );

    // -- Fill total_amount (number input) --
    const amountInput = screen.getByRole("spinbutton", {
      name: /valor total/i,
    });
    fireEvent.change(amountInput, { target: { value: "1500" } });

    // -- Fill description --
    await user.type(
      screen.getByRole("textbox", { name: /descrição/i }),
      "Descrição do contrato de teste",
    );

    // -- Submit --
    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(createFullAsync).toHaveBeenCalled();
    });

    expect(createFullAsync).toHaveBeenCalledWith({
      data: {
        wedding: weddingUuid,
        supplier: "supplier-1",
        name: "Contrato Teste",
        total_amount: 1500,
        status: "DRAFT",
        description: "Descrição do contrato de teste",
        parent: null,
        items_data: "[]",
        create_expense: false,
        expense_category: null,
        expense_num_installments: null,
        expense_first_due_date: null,
        pdf_file: null,
      },
    });
  });

  // ------------------------------------------------------------------
  // 6. Shows success toast on successful creation
  // ------------------------------------------------------------------
  it("shows success toast on successful creation", async () => {
    const user = userEvent.setup();

    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [mockSupplier], count: 1 } }),
    );

    render(<ContractUploadDialog {...defaultProps} />);

    // Select supplier
    await user.click(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    );
    const supplierOption = await screen.findByRole("option", {
      name: /fornecedor teste/i,
    });
    await user.click(supplierOption);

    // Fill required fields
    await user.type(
      screen.getByRole("textbox", { name: /nome do contrato/i }),
      "Teste",
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: /valor total/i }),
      { target: { value: "1000" } },
    );

    // Submit
    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(toastSuccess).toHaveBeenCalledWith(
        "Contrato criado com sucesso!",
      );
    });

    // onSuccess callback should have been called
    expect(onSuccess).toHaveBeenCalled();
  });

  // ------------------------------------------------------------------
  // 7. Shows error toast on API failure
  // ------------------------------------------------------------------
  it("shows error toast on API failure", async () => {
    const user = userEvent.setup();

    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [mockSupplier], count: 1 } }),
    );


    createFullAsync.mockRejectedValue(new Error("API Error"));

    render(<ContractUploadDialog {...defaultProps} />);


    await user.click(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    );
    const supplierOption = await screen.findByRole("option", {
      name: /fornecedor teste/i,
    });
    await user.click(supplierOption);


    await user.type(
      screen.getByRole("textbox", { name: /nome do contrato/i }),
      "Falha",
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: /valor total/i }),
      { target: { value: "500" } },
    );


    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(toastError).toHaveBeenCalled();
    });
  });

  it("submits with parent contract", async () => {
    const user = userEvent.setup();

    mockSuppliersList.mockReturnValue(
      mockQueryResponse({ data: { items: [mockSupplier], count: 1 } }),
    );
    mockContractsList.mockReturnValue(
      mockQueryResponse({
        data: {
          items: [{ uuid: "parent-1", name: "Contrato Original" }],
          count: 1,
        },
      }),
    );

    render(
      <ContractUploadDialog
        {...defaultProps}
        prefilledParentUuid="parent-1"
      />,
    );

    await user.click(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    );
    const supplierOption = await screen.findByRole("option", {
      name: /fornecedor teste/i,
    });
    await user.click(supplierOption);

    await user.type(
      screen.getByRole("textbox", { name: /nome do contrato/i }),
      "Aditivo",
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: /valor total/i }),
      { target: { value: "1000" } },
    );

    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(createFullAsync).toHaveBeenCalled();
    });

    expect(createFullAsync).toHaveBeenCalledWith({
      data: expect.objectContaining({
        parent: "parent-1",
      }),
    });
  });

  it("shows loading state while creating", () => {
    mockCreateFull.mockReturnValue({
      mutateAsync: createFullAsync,
      isPending: true,
    });

    render(<ContractUploadDialog {...defaultProps} />);

    expect(screen.getByRole("button", { name: /criar contrato/i })).toBeDisabled();
    expect(screen.getByText(/cancelar/i).closest("button")).toBeDisabled();
  });
});
