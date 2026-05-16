import { describe, expect, it } from "vitest";
import { useSupplierFormDialogState } from "@/features/logistics/hooks/useSupplierFormDialogState";
import { renderHook, act } from "@/test-utils";
import { createMockSupplier } from "@/test-data";

const mockSupplier = createMockSupplier({ uuid: "supplier-1" });

describe("useSupplierFormDialogState", () => {
  it("starts with dialog closed and no supplier", () => {
    const { result } = renderHook(() => useSupplierFormDialogState());

    expect(result.current.formOpen).toBe(false);
    expect(result.current.formMode).toBe("create");
    expect(result.current.editingSupplier).toBeNull();
  });

  it("openCreateDialog opens dialog in create mode", () => {
    const { result } = renderHook(() => useSupplierFormDialogState());

    act(() => {
      result.current.openCreateDialog();
    });

    expect(result.current.formOpen).toBe(true);
    expect(result.current.formMode).toBe("create");
    expect(result.current.editingSupplier).toBeNull();
  });

  it("openEditDialog opens dialog with supplier data", () => {
    const { result } = renderHook(() => useSupplierFormDialogState());

    act(() => {
      result.current.openEditDialog(mockSupplier);
    });

    expect(result.current.formOpen).toBe(true);
    expect(result.current.formMode).toBe("edit");
    expect(result.current.editingSupplier).toEqual(mockSupplier);
  });

  it("setFormOpen can close the dialog", () => {
    const { result } = renderHook(() => useSupplierFormDialogState());

    act(() => {
      result.current.openCreateDialog();
    });
    expect(result.current.formOpen).toBe(true);

    act(() => {
      result.current.setFormOpen(false);
    });
    expect(result.current.formOpen).toBe(false);
  });
});
