import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { useSupplierMutations } from "@/features/logistics/hooks/useSupplierMutations";
import { EMPTY_SUPPLIER_FORM_STATE } from "@/features/logistics/types";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { createMockSupplier } from "@/test-data";
import { server } from "@/mocks/server";

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

const mockSupplier = createMockSupplier();

function renderMutationsHook({
  formMode,
  formState,
  supplierToDelete = null,
}: {
  formMode: "create" | "edit";
  formState: typeof EMPTY_SUPPLIER_FORM_STATE & { uuid?: string };
  supplierToDelete?: SupplierOut | null;
}) {
  const setFormOpen = vi.fn();
  const setSupplierToDelete = vi.fn();
  const refetchSuppliers = vi.fn().mockResolvedValue(undefined);

  return renderHook(
    () =>
      useSupplierMutations({
        formMode,
        formState,
        supplierToDelete,
        setFormOpen,
        setSupplierToDelete,
        refetchSuppliers,
      }),
  );
}

describe("useSupplierMutations", () => {
  it("shows error when form is invalid", async () => {
    const { result } = renderMutationsHook({
      formMode: "create",
      formState: { ...EMPTY_SUPPLIER_FORM_STATE, name: "" },
    });

    await act(async () => {
      await result.current.handleSaveSupplier();
    });

    expect(toastError).toHaveBeenCalledWith(
      "Informe o nome do fornecedor.",
    );
  });

  it("shows success toast on create", async () => {
    const { result } = renderMutationsHook({
      formMode: "create",
      formState: {
        name: "Novo Fornecedor",
        cnpj: "12.345.678/0001-90",
        phone: "(11) 99999-0000",
        email: "novo@email.com",
        status: "active",
      },
    });

    await act(async () => {
      await result.current.handleSaveSupplier();
    });

    expect(toastSuccess).toHaveBeenCalledWith(
      "Fornecedor criado com sucesso!",
    );
  });

  it("shows success toast on delete", async () => {
    const { result } = renderMutationsHook({
      formMode: "create",
      formState: { ...EMPTY_SUPPLIER_FORM_STATE },
      supplierToDelete: mockSupplier,
    });

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toastSuccess).toHaveBeenCalledWith(
      "Fornecedor removido com sucesso!",
    );
  });

  it("does not attempt delete when supplierToDelete is null", async () => {
    const { result } = renderMutationsHook({
      formMode: "create",
      formState: { ...EMPTY_SUPPLIER_FORM_STATE },
      supplierToDelete: null,
    });

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toastSuccess).not.toHaveBeenCalled();
    expect(toastError).not.toHaveBeenCalled();
  });

  it("shows error toast on API failure when saving", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/logistics/suppliers/", () =>
        HttpResponse.json({ detail: "CNPJ duplicado" }, { status: 409 }),
      ),
    );

    const { result } = renderMutationsHook({
      formMode: "create",
      formState: {
        name: "Fornecedor Erro",
        cnpj: "12.345.678/0001-90",
        phone: "(11) 99999-0000",
        email: "erro@email.com",
        status: "active",
      },
    });

    await act(async () => {
      await result.current.handleSaveSupplier();
    });

    expect(toastError).toHaveBeenCalledWith("CNPJ duplicado");
  });
});
