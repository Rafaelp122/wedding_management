import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { SuppliersTable } from "@/features/logistics/components/suppliers/SuppliersTable";
import { createMockSupplier } from "@/test-data";

const mockSuppliers = [
  createMockSupplier({ uuid: "s-1", name: "Buffet Gourmet", email: "buffet@email.com" }),
  createMockSupplier({ uuid: "s-2", name: "Fotógrafo Arte", email: "foto@email.com", is_active: false }),
];

describe("SuppliersTable", () => {
  it("renders supplier rows", () => {
    render(
      <SuppliersTable
        suppliers={mockSuppliers}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />,
    );

    expect(screen.getByText("Buffet Gourmet")).toBeInTheDocument();
    expect(screen.getByText("Fotógrafo Arte")).toBeInTheDocument();
    expect(screen.getByText("buffet@email.com")).toBeInTheDocument();
  });

  it("renders status badges", () => {
    render(
      <SuppliersTable
        suppliers={mockSuppliers}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />,
    );

    expect(screen.getByText("Ativo")).toBeInTheDocument();
    expect(screen.getByText("Inativo")).toBeInTheDocument();
  });

  it("shows dash for empty fields", () => {
    render(
      <SuppliersTable
        suppliers={[
          createMockSupplier({ phone: "", email: "" }),
        ]}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
      />,
    );

    const dashes = screen.getAllByText("—");
    expect(dashes.length).toBeGreaterThanOrEqual(2);
  });

  it("calls onEdit when edit is clicked", async () => {
    const onEdit = vi.fn();
    render(
      <SuppliersTable
        suppliers={mockSuppliers}
        onEdit={onEdit}
        onDelete={vi.fn()}
      />,
    );

    const actionButtons = screen.getAllByRole("button", { name: /ações/i });
    const user = userEvent.setup();
    await user.click(actionButtons[0]);

    const editOption = screen.getByText("Editar");
    await user.click(editOption);

    expect(onEdit).toHaveBeenCalledWith(mockSuppliers[0]);
  });

  it("calls onDetail when row is clicked", async () => {
    const onDetail = vi.fn();
    render(
      <SuppliersTable
        suppliers={mockSuppliers}
        onEdit={vi.fn()}
        onDelete={vi.fn()}
        onDetail={onDetail}
      />,
    );

    const rows = screen.getAllByRole("row");
    const user = userEvent.setup();
    await user.click(rows[1]);

    expect(onDetail).toHaveBeenCalledWith("s-1");
  });
});
