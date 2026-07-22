import { HttpResponse, http } from "msw";
import { toast } from "sonner";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { act, renderHook, server, waitFor } from "@/test-utils";
import { useCreateExpenseForm } from "./useCreateExpenseForm";

describe("useCreateExpenseForm", () => {
  const weddingUuid = "wedding-1";
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  const mockCategory = {
    uuid: "cat-1",
    name: "Alimentação",
  };

  const mockContract = {
    uuid: "contract-1",
    description: "Contrato Buffet",
  };

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      http.get("*/api/v1/finances/categories/", () => {
        return HttpResponse.json({ items: [mockCategory], count: 1 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [mockContract], count: 1 });
      }),
      http.post("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ uuid: "expense-1" }, { status: 201 });
      }),
    );
  });

  it("fetches categories and contracts and initializes default values", async () => {
    const { result } = renderHook(() =>
      useCreateExpenseForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    expect(result.current.form.getValues("category")).toBe("");
    expect(result.current.form.getValues("num_installments")).toBe(1);

    await waitFor(() => {
      expect(result.current.categories).toHaveLength(1);
      expect(result.current.contracts).toHaveLength(1);
    });
  });

  it("resets form when handleOpenChange is called with false", async () => {
    const { result } = renderHook(() =>
      useCreateExpenseForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    act(() => {
      result.current.form.setValue("name", "Despesa Teste");
    });
    expect(result.current.form.getValues("name")).toBe("Despesa Teste");

    act(() => {
      result.current.handleOpenChange(false);
    });

    expect(onOpenChange).toHaveBeenCalledWith(false);
    expect(result.current.form.getValues("name")).toBe("");
  });

  it("submits form data successfully", async () => {
    let submittedBody: unknown;
    server.use(
      http.post("*/api/v1/finances/expenses/", async ({ request }) => {
        submittedBody = await request.json();
        return HttpResponse.json({ uuid: "expense-1" }, { status: 201 });
      }),
    );

    const { result } = renderHook(() =>
      useCreateExpenseForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    const formData = {
      category: "cat-1",
      contract: "contract-1",
      name: "Bolo de Casamento",
      description: "Bolo de 3 andares",
      estimated_amount: 1200,
      actual_amount: 1200,
      num_installments: 2,
      first_due_date: "2026-10-01",
    };

    act(() => {
      result.current.onSubmit(formData);
    });

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Despesa criada com sucesso!");
      expect(onSuccess).toHaveBeenCalled();
    });

    expect(submittedBody).toMatchObject(formData);
  });

  it("shows error toast when creation fails", async () => {
    server.use(
      http.post("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
      }),
    );

    const { result } = renderHook(() =>
      useCreateExpenseForm({
        weddingUuid,
        onOpenChange,
        onSuccess,
      }),
    );

    act(() => {
      result.current.onSubmit({
        category: "cat-1",
        contract: null,
        name: "Erro",
        description: "",
        estimated_amount: 100,
        actual_amount: 100,
        num_installments: 1,
        first_due_date: "2026-10-01",
      });
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro interno");
    });
  });
});
