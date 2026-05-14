import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { DeleteSupplierDialog } from "@/features/logistics/components/suppliers/DeleteSupplierDialog";
import { createMockSupplier } from "@/test-data";

const mockSupplier = createMockSupplier();

describe("DeleteSupplierDialog", () => {
  it("renders nothing when supplier is null", () => {
    render(
      <DeleteSupplierDialog
        supplier={null}
        isDeleting={false}
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );

    expect(
      screen.queryByText("Excluir fornecedor"),
    ).not.toBeInTheDocument();
  });

  it("renders supplier name when open", () => {
    render(
      <DeleteSupplierDialog
        supplier={mockSupplier}
        isDeleting={false}
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );

    expect(screen.getByText("Fornecedor Teste")).toBeInTheDocument();
  });

  it("calls onConfirm when delete button is clicked", async () => {
    const onConfirm = vi.fn();
    render(
      <DeleteSupplierDialog
        supplier={mockSupplier}
        isDeleting={false}
        onCancel={vi.fn()}
        onConfirm={onConfirm}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /^excluir$/i }));
    expect(onConfirm).toHaveBeenCalled();
  });

  it("disables delete button when isDeleting is true", () => {
    render(
      <DeleteSupplierDialog
        supplier={mockSupplier}
        isDeleting={true}
        onCancel={vi.fn()}
        onConfirm={vi.fn()}
      />,
    );

    expect(
      screen.getByRole("button", { name: /excluindo/i }),
    ).toBeDisabled();
  });
});
