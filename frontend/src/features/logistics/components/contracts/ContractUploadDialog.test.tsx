import { beforeEach, describe, expect, it, vi, beforeAll } from "vitest";
import { fireEvent, render, screen, userEvent, waitFor } from "@/test-utils";
import { ContractUploadDialog } from "./ContractUploadDialog";
import { toast } from "sonner";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

beforeAll(() => {
  Element.prototype.hasPointerCapture ??= () => false;
  Element.prototype.setPointerCapture ??= () => {};
  Element.prototype.releasePointerCapture ??= () => {};
  Element.prototype.scrollIntoView ??= () => {};
});

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
    vi.unstubAllGlobals();

    server.use(
      http.get("*/api/v1/finances/categories/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ uuid: "contract-1" }, { status: 201 });
      }),
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        return HttpResponse.json({
          upload_url: "https://r2.example.com/upload",
          object_key: "r2-file-key",
        });
      })
    );
  });

  it("renders nothing when closed", () => {
    render(<ContractUploadDialog {...defaultProps} open={false} />);

    expect(screen.queryByText("Novo Contrato")).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /criar contrato/i }),
    ).not.toBeInTheDocument();
  });

  it("renders form fields when open", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(screen.getByText("Novo Contrato")).toBeInTheDocument();
    expect(
      screen.getByText(
        "Vincule um fornecedor a este evento com um novo contrato.",
      ),
    ).toBeInTheDocument();

    expect(screen.getByText("Fornecedor")).toBeInTheDocument();
    expect(screen.getByText("Nome do Contrato")).toBeInTheDocument();
    expect(screen.getByText("Valor Total")).toBeInTheDocument();
    expect(screen.getByText("Status")).toBeInTheDocument();
    expect(screen.getByText("Descrição")).toBeInTheDocument();

    expect(
      screen.getByPlaceholderText("Ex: Buffet Completo"),
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("Descreva o objeto do contrato..."),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("combobox", { name: /fornecedor/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("combobox", { name: /status/i }),
    ).toBeInTheDocument();

    expect(
      screen.getByText(/este sistema não substitui consultoria jurídica/i),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("button", { name: /cancelar/i }),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /criar contrato/i }),
    ).toBeInTheDocument();
  });

  it("renders item drafts section", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(screen.getByText("Itens (Opcional)")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /adicionar/i }),
    ).toBeInTheDocument();
    expect(screen.getByText("Nenhum item adicionado.")).toBeInTheDocument();
  });

  it("renders expense creation checkbox section", () => {
    render(<ContractUploadDialog {...defaultProps} />);

    expect(
      screen.getByText("Criar despesa a partir deste contrato"),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("checkbox", { name: /criar despesa/i }),
    ).toBeInTheDocument();
  });

  it("fills form and submits successfully", async () => {
    const user = userEvent.setup();
    const mockMutateAsync = vi.fn();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        const body = await request.json();
        mockMutateAsync(body);
        return HttpResponse.json({ uuid: "contract-1" }, { status: 201 });
      })
    );

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
      "Contrato Teste",
    );

    const amountInput = screen.getByRole("spinbutton", {
      name: /valor total/i,
    });
    fireEvent.change(amountInput, { target: { value: "1500" } });

    await user.type(
      screen.getByRole("textbox", { name: /descrição/i }),
      "Descrição do contrato de teste",
    );

    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(mockMutateAsync).toHaveBeenCalled();
    });

    expect(mockMutateAsync).toHaveBeenCalledWith(
      expect.objectContaining({
        wedding: weddingUuid,
        supplier: "supplier-1",
        name: "Contrato Teste",
        total_amount: 1500,
        status: "DRAFT",
        description: "Descrição do contrato de teste",
        parent: null,
        pdf_file_key: null,
      })
    );
  });

  it("shows success toast on successful creation", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      })
    );

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
      "Teste",
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: /valor total/i }),
      { target: { value: "1000" } },
    );

    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Contrato criado com sucesso!",
      );
    });

    expect(onSuccess).toHaveBeenCalled();
  });

  it("shows error toast on API failure", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ detail: "API Error" }, { status: 500 });
      })
    );

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
      expect(toast.error).toHaveBeenCalledWith(
        "Erro ao criar contrato: Request failed with status code 500",
      );
    });
  });

  it("submits with parent contract", async () => {
    const user = userEvent.setup();
    const mockMutateAsync = vi.fn();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        const body = await request.json();
        mockMutateAsync(body);
        return HttpResponse.json({ uuid: "contract-1" }, { status: 201 });
      })
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
      expect(mockMutateAsync).toHaveBeenCalled();
    });

    expect(mockMutateAsync).toHaveBeenCalledWith(
      expect.objectContaining({
        parent: "parent-1",
      }),
    );
  });

  it("shows loading state while creating", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", async () => {
        // Atrasar resposta indefinidamente para manter em loading
        await new Promise(() => {});
        return HttpResponse.json({ uuid: "contract-1" });
      })
    );

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
      "Teste",
    );
    fireEvent.change(
      screen.getByRole("spinbutton", { name: /valor total/i }),
      { target: { value: "1000" } },
    );

    await user.click(
      screen.getByRole("button", { name: /criar contrato/i }),
    );

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /criar contrato/i })).toBeDisabled();
    });
    expect(screen.getByText(/cancelar/i).closest("button")).toBeDisabled();
  });

  it("uploads file to R2 and submits pdf_file_key", async () => {
    const user = userEvent.setup();
    const mockGetUploadUrl = vi.fn();
    const mockCreateFull = vi.fn();

    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/upload-url/", async ({ request }) => {
        const body = await request.json();
        mockGetUploadUrl(body);
        return HttpResponse.json({
          upload_url: "https://r2.example.com/upload",
          object_key: "r2-file-key",
        });
      }),
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        const body = await request.json();
        mockCreateFull(body);
        return HttpResponse.json({ uuid: "contract-1" }, { status: 201 });
      })
    );

    // Mock global fetch para simular o upload para o R2
    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
    } as Response);
    vi.stubGlobal("fetch", mockFetch);

    render(<ContractUploadDialog {...defaultProps} />);

    await user.click(screen.getByRole("combobox", { name: /fornecedor/i }));
    const supplierOption = await screen.findByRole("option", {
      name: /fornecedor teste/i,
    });
    await user.click(supplierOption);

    await user.type(
      screen.getByRole("textbox", { name: /nome do contrato/i }),
      "Contrato com PDF",
    );

    const amountInput = screen.getByRole("spinbutton", {
      name: /valor total/i,
    });
    fireEvent.change(amountInput, { target: { value: "2500" } });

    const file = new File(["dummy content"], "contract.pdf", {
      type: "application/pdf",
    });
    const fileInput = document.body.querySelector(
      'input[type="file"]',
    ) as HTMLInputElement;
    await user.upload(fileInput, file);

    await user.click(screen.getByRole("button", { name: /criar contrato/i }));

    await waitFor(() => {
      expect(mockGetUploadUrl).toHaveBeenCalledWith(
        expect.objectContaining({
          filename: "contract.pdf",
          wedding_id: weddingUuid,
        })
      );
      expect(mockCreateFull).toHaveBeenCalledWith(
        expect.objectContaining({
          name: "Contrato com PDF",
          pdf_file_key: "r2-file-key",
        })
      );
    });
  });
});
