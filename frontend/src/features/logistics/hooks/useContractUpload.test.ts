import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { useContractUpload } from "./useContractUpload";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";

describe("useContractUpload", () => {
  const weddingUuid = "wedding-uuid-abc";
  const mockOnSuccess = vi.fn();

  const defaultFormData = {
    wedding: weddingUuid,
    supplier: "supplier-uuid-123",
    name: "Contrato de Flores",
    total_amount: 1500,
    status: "active" as const,
    description: "Serviço de decoração e arranjos florais",
    parent: null,
  };

  const defaultExpense = {
    checked: false,
    category: "decoration",
    numInstallments: 1,
    firstDueDate: "2026-08-01",
  };

  it("should create a contract successfully without file upload", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    // Intercept full contract creation API
    server.use(
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ uuid: "new-contract-uuid" }, { status: 201 });
      })
    );

    let success = false;
    await act(async () => {
      success = await result.current.uploadAndCreateContract(
        defaultFormData,
        null, // no file
        [], // no items
        defaultExpense
      );
    });

    expect(success).toBe(true);
    expect(toast.success).toHaveBeenCalledWith("Contrato criado com sucesso!");
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it("should upload file and create contract successfully when selectedFile is provided", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    // Mock file to upload
    const file = new File(["dummy content"], "contrato.pdf", {
      type: "application/pdf",
    });

    // Intercept getUploadUrl
    server.use(
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        return HttpResponse.json(
          {
            upload_url: "https://mock-upload-s3.com/contrato.pdf",
            object_key: "contracts/object-key-123.pdf",
          },
          { status: 200 }
        );
      })
    );

    // Intercept the PUT file upload to S3/R2 URL
    server.use(
      http.put("https://mock-upload-s3.com/contrato.pdf", () => {
        return new HttpResponse(null, { status: 200 });
      })
    );

    // Intercept full contract creation API
    let capturedBody: Record<string, unknown> | null = null;
    server.use(
      http.post("*/api/v1/logistics/contracts/full/", async ({ request }) => {
        capturedBody = (await request.json()) as Record<string, unknown>;
        return HttpResponse.json({ uuid: "new-contract-uuid" }, { status: 201 });
      })
    );

    let success = false;
    await act(async () => {
      success = await result.current.uploadAndCreateContract(
        defaultFormData,
        file,
        [{ name: "Arranjo de Mesa", quantity: 10, acquisition_status: "pending" }],
        { ...defaultExpense, checked: true }
      );
    });

    expect(success).toBe(true);
    expect(toast.success).toHaveBeenCalledWith("Contrato criado com sucesso!");
    expect(mockOnSuccess).toHaveBeenCalled();
    expect(capturedBody).not.toBeNull();
    expect(capturedBody!.pdf_file_key).toBe("contracts/object-key-123.pdf");
    expect(capturedBody!.create_expense).toBe(true);
    expect(JSON.parse(capturedBody!.items_data as string)).toEqual([
      { name: "Arranjo de Mesa", quantity: 10, acquisition_status: "pending" },
    ]);
  });

  it("should show error toast and return false when getUploadUrl fails", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    const file = new File(["dummy content"], "contrato.pdf", {
      type: "application/pdf",
    });

    server.use(
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        return HttpResponse.json({ detail: "Sem permissão" }, { status: 403 });
      })
    );

    let success = true;
    await act(async () => {
      success = await result.current.uploadAndCreateContract(
        defaultFormData,
        file,
        [],
        defaultExpense
      );
    });

    expect(success).toBe(false);
    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining("Erro ao criar contrato: Request failed with status code 403")
    );
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("should show error toast and return false when PUT file upload fails", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    const file = new File(["dummy content"], "contrato.pdf", {
      type: "application/pdf",
    });

    server.use(
      http.post("*/api/v1/logistics/contracts/upload-url/", () => {
        return HttpResponse.json(
          {
            upload_url: "https://mock-upload-s3.com/contrato.pdf",
            object_key: "contracts/object-key-123.pdf",
          },
          { status: 200 }
        );
      })
    );

    // Mock PUT to return 500 error
    server.use(
      http.put("https://mock-upload-s3.com/contrato.pdf", () => {
        return new HttpResponse(null, { status: 500, statusText: "Internal Server Error" });
      })
    );

    let success = true;
    await act(async () => {
      success = await result.current.uploadAndCreateContract(
        defaultFormData,
        file,
        [],
        defaultExpense
      );
    });

    expect(success).toBe(false);
    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining("Erro ao criar contrato: Erro no envio do arquivo: Internal Server Error")
    );
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("should show error toast and return false when contract creation API fails", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    server.use(
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ detail: "Erro de validação" }, { status: 400 });
      })
    );

    let success = true;
    await act(async () => {
      success = await result.current.uploadAndCreateContract(
        defaultFormData,
        null,
        [],
        defaultExpense
      );
    });

    expect(success).toBe(false);
    expect(toast.error).toHaveBeenCalledWith(
      expect.stringContaining("Erro ao criar contrato: Request failed with status code 400")
    );
    expect(mockOnSuccess).not.toHaveBeenCalled();
  });

  it("should manage isPending state correctly throughout the execution", async () => {
    const { result } = renderHook(() =>
      useContractUpload({ weddingUuid, onSuccess: mockOnSuccess })
    );

    server.use(
      http.post("*/api/v1/logistics/contracts/full/", () => {
        return HttpResponse.json({ uuid: "new-contract-uuid" }, { status: 201 });
      })
    );

    expect(result.current.isPending).toBe(false);

    let promise: Promise<boolean>;
    act(() => {
      promise = result.current.uploadAndCreateContract(
        defaultFormData,
        null,
        [],
        defaultExpense
      );
    });

    expect(result.current.isPending).toBe(true);

    await act(async () => {
      await promise;
    });

    expect(result.current.isPending).toBe(false);
  });
});
