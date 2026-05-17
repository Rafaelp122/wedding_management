import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { useSupplierMutations } from "@/features/logistics/hooks/useSupplierMutations";
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

function renderMutationsHook(supplierToDelete: SupplierOut | null = mockSupplier) {
  const setSupplierToDelete = vi.fn();
  const refetchSuppliers = vi.fn().mockResolvedValue(undefined);

  return renderHook(() =>
    useSupplierMutations({
      supplierToDelete,
      setSupplierToDelete,
      refetchSuppliers,
    }),
  );
}

describe("useSupplierMutations", () => {
  it("shows success toast on delete", async () => {
    const { result } = renderMutationsHook();

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toastSuccess).toHaveBeenCalledWith(
      "Fornecedor removido com sucesso!",
    );
  });

  it("does not attempt delete when supplierToDelete is null", async () => {
    const { result } = renderMutationsHook(null);

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toastSuccess).not.toHaveBeenCalled();
    expect(toastError).not.toHaveBeenCalled();
  });

  it("shows error toast on API failure when deleting", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.delete("*/api/v1/logistics/suppliers/*", () =>
        HttpResponse.json({ detail: "Fornecedor não encontrado" }, { status: 404 }),
      ),
    );

    const { result } = renderMutationsHook();

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toastError).toHaveBeenCalledWith(
      "Fornecedor não encontrado",
    );
  });
});
