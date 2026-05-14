import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
import { SupplierFormDialog } from "@/features/logistics/components/suppliers/SupplierFormDialog";
import { EMPTY_SUPPLIER_FORM_STATE, type SupplierFormState } from "@/features/logistics/types";

const editState: SupplierFormState = {
  uuid: "s-1",
  name: "Fornecedor X",
  cnpj: "12.345.678/0001-90",
  phone: "(11) 99999-0000",
  email: "contato@fornecedor.com",
  status: "active",
};

describe("SupplierFormDialog", () => {
  it("renders create dialog with empty fields", () => {
    render(
      <SupplierFormDialog
        open={true}
        mode="create"
        formState={EMPTY_SUPPLIER_FORM_STATE}
        setFormState={vi.fn()}
        isSaving={false}
        onOpenChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    expect(screen.getByText("Novo fornecedor")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.getByLabelText("Telefone")).toBeInTheDocument();
    expect(screen.getByLabelText("CNPJ")).toBeInTheDocument();
  });

  it("renders edit dialog with pre-filled data", () => {
    render(
      <SupplierFormDialog
        open={true}
        mode="edit"
        formState={editState}
        setFormState={vi.fn()}
        isSaving={false}
        onOpenChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    expect(screen.getByText("Editar fornecedor")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("Fornecedor X");
    expect(screen.getByLabelText("CNPJ")).toHaveValue("12.345.678/0001-90");
  });

  it("calls onSave when save button is clicked", async () => {
    const onSave = vi.fn();
    render(
      <SupplierFormDialog
        open={true}
        mode="create"
        formState={EMPTY_SUPPLIER_FORM_STATE}
        setFormState={vi.fn()}
        isSaving={false}
        onOpenChange={vi.fn()}
        onSave={onSave}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /salvar/i }));
    expect(onSave).toHaveBeenCalled();
  });

  it("disables save button when isSaving is true", () => {
    render(
      <SupplierFormDialog
        open={true}
        mode="create"
        formState={EMPTY_SUPPLIER_FORM_STATE}
        setFormState={vi.fn()}
        isSaving={true}
        onOpenChange={vi.fn()}
        onSave={vi.fn()}
      />,
    );

    const saveBtn = screen.getByRole("button", { name: /salvando/i });
    expect(saveBtn).toBeDisabled();
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    render(
      <SupplierFormDialog
        open={true}
        mode="create"
        formState={EMPTY_SUPPLIER_FORM_STATE}
        setFormState={vi.fn()}
        isSaving={false}
        onOpenChange={onOpenChange}
        onSave={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });
});
