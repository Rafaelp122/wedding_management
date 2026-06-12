import { describe, expect, it, vi } from "vitest";
import { renderHook, act } from "@/test-utils";
import { useSupplierMutations } from "@/features/logistics/hooks/useSupplierMutations";
import type { SupplierOut } from "@/api/generated/v1/models/supplierOut";
import { createMockSupplier } from "@/test-data";
import { server } from "@/mocks/server";
import { toast } from "sonner";

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

    expect(toast.success).toHaveBeenCalledWith(
      "Fornecedor removido com sucesso!",
    );
  });

  it("does not attempt delete when supplierToDelete is null", async () => {
    const { result } = renderMutationsHook(null);

    await act(async () => {
      await result.current.handleDeleteSupplier();
    });

    expect(toast.success).not.toHaveBeenCalled();
    expect(toast.error).not.toHaveBeenCalled();
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

    expect(toast.error).toHaveBeenCalledWith(
      "Fornecedor não encontrado",
    );
  });
});
