import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { useContractUploadForm } from "./useContractUploadForm";

describe("useContractUploadForm", () => {
  const weddingUuid = "wedding-1";
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  const mockSupplier = {
    uuid: "supplier-1",
    name: "Fornecedor Teste",
  };

  const mockContract = {
    uuid: "contract-parent",
    name: "Contrato Pai",
  };

  const mockCategory = {
    uuid: "category-1",
    name: "Decoração",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/logistics/suppliers/", () => {
        return HttpResponse.json({ items: [mockSupplier], count: 1 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [mockContract], count: 1 });
      }),
      http.get("*/api/v1/finances/categories/", () => {
        return HttpResponse.json({ items: [mockCategory], count: 1 });
      }),
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ uuid: "contract-new" }, { status: 201 });
      }),
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        return HttpResponse.json({
          upload_url: "https://r2.example.com/upload",
          object_key: "r2-file-key",
        });
      }),
    );
  });

  it("fetches data and initializes form with defaults", async () => {
    const { result } = renderHook(() =>
      useContractUploadForm({
        weddingUuid,
        prefilledParentUuid: "contract-parent",
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.form.getValues()).toMatchObject({
      wedding: weddingUuid,
      supplier: "",
      name: "",
      status: "DRAFT",
      parent: "contract-parent",
    });

    await waitFor(() => {
      expect(result.current.suppliers).toHaveLength(1);
      expect(result.current.existingContracts).toHaveLength(1);
      expect(result.current.categories).toHaveLength(1);
    });
  });

  it("resets form, selected file, and item drafts on close", async () => {
    const { result } = renderHook(() =>
      useContractUploadForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    const file = new File(["test"], "test.pdf", { type: "application/pdf" });
    act(() => {
      result.current.setSelectedFile(file);
      result.current.setItemDrafts([
        { key: "1", name: "Item 1", quantity: 2, acquisition_status: "PENDING" },
      ]);
    });

    expect(result.current.selectedFile).toBe(file);
    expect(result.current.itemDrafts).toHaveLength(1);

    act(() => {
      result.current.handleOpenChange(false);
    });

    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(result.current.selectedFile).toBeNull();
    expect(result.current.itemDrafts).toEqual([]);
  });

  it("submits form data successfully without file", async () => {
    let submittedPayload: unknown;
    server.use(
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        submittedPayload = await request.json();
        return HttpResponse.json({ uuid: "contract-new" }, { status: 201 });
      }),
    );

    const { result } = renderHook(() =>
      useContractUploadForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    act(() => {
      result.current.handleExpenseChange({
        checked: true,
        category: "category-1",
        numInstallments: 3,
        firstDueDate: "2026-09-01",
      });
      result.current.setItemDrafts([
        { key: "1", name: "Mesas", quantity: 10, acquisition_status: "PENDING" },
      ]);
    });

    const formData = {
      wedding: weddingUuid,
      supplier: "supplier-1",
      name: "Novo Contrato",
      total_amount: 5000,
      status: "DRAFT" as const,
      description: "Descrição",
      parent: null,
    };

    await act(async () => {
      await result.current.onSubmit(formData);
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato criado com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });

    expect(submittedPayload).toMatchObject({
      wedding: weddingUuid,
      supplier: "supplier-1",
      name: "Novo Contrato",
      total_amount: 5000,
      create_expense: true,
      expense_category: "category-1",
      expense_num_installments: 3,
      expense_first_due_date: "2026-09-01",
      pdf_file_key: null,
    });
  });

  it("uploads file to R2 when selectedFile exists", async () => {
    let uploadUrlRequested = false;
    let submittedPayload: Record<string, unknown> | undefined;

    server.use(
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        uploadUrlRequested = true;
        return HttpResponse.json({
          upload_url: "https://r2.example.com/upload",
          object_key: "uploaded-pdf-key",
        });
      }),
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        submittedPayload = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ uuid: "contract-new" }, { status: 201 });
      }),
    );

    const mockFetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
    } as Response);
    vi.stubGlobal("fetch", mockFetch);

    const { result } = renderHook(() =>
      useContractUploadForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    const file = new File(["pdf data"], "doc.pdf", { type: "application/pdf" });
    act(() => {
      result.current.setSelectedFile(file);
    });

    const formData = {
      wedding: weddingUuid,
      supplier: "supplier-1",
      name: "Contrato com PDF",
      total_amount: 3000,
      status: "DRAFT" as const,
      description: "",
      parent: null,
    };

    await act(async () => {
      await result.current.onSubmit(formData);
    });

    await waitFor(() => {
      expect(uploadUrlRequested).toBe(true);
      expect(toast.success).toHaveBeenCalled();
    });

    expect(submittedPayload?.pdf_file_key).toBe("uploaded-pdf-key");
  });

  it("handles errors during submission", async () => {
    server.use(
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
      }),
    );

    const { result } = renderHook(() =>
      useContractUploadForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    const formData = {
      wedding: weddingUuid,
      supplier: "supplier-1",
      name: "Contrato com Erro",
      total_amount: 1000,
      status: "DRAFT" as const,
      description: "",
      parent: null,
    };

    await act(async () => {
      await result.current.onSubmit(formData);
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining("Erro ao criar contrato: Request failed with status code 500"),
      );
    });
  });
});
