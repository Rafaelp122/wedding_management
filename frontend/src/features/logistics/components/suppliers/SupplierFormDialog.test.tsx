import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { SupplierFormDialog } from "@/features/logistics/components/suppliers/SupplierFormDialog";
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

const mockSupplier = createMockSupplier({
  uuid: "s-edit",
  address: "Rua das Rosas, 123",
  city: "São Paulo",
  state: "SP",
  website: "https://buffet.com.br",
  notes: "Fornecedor premium",
});

describe("SupplierFormDialog", () => {
  it("renders create dialog with empty fields", () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Novo fornecedor")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toBeInTheDocument();
    expect(screen.getByLabelText("E-mail")).toBeInTheDocument();
    expect(screen.getByLabelText("Telefone")).toBeInTheDocument();
    expect(screen.getByLabelText("CNPJ")).toBeInTheDocument();
  });

  it("renders all optional fields in create mode", () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Endereço")).toBeInTheDocument();
    expect(screen.getByLabelText("Cidade")).toBeInTheDocument();
    expect(screen.getByLabelText("Estado (UF)")).toBeInTheDocument();
    expect(screen.getByLabelText("Website")).toBeInTheDocument();
    expect(screen.getByLabelText("Observações")).toBeInTheDocument();
  });

  it("applies CNPJ mask as user types digits", async () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    const cnpjInput = screen.getByLabelText("CNPJ");

    await user.type(cnpjInput, "12345678000190");
    expect(cnpjInput).toHaveValue("12.345.678/0001-90");
  });

  it("limits CNPJ to 14 digits", async () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    const cnpjInput = screen.getByLabelText("CNPJ");

    await user.type(cnpjInput, "1234567800019012345");
    expect((cnpjInput as HTMLInputElement).value).toHaveLength(18);
  });

  it("renders edit dialog with pre-filled data", () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="edit"
        supplier={mockSupplier}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByText("Editar fornecedor")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome")).toHaveValue("Fornecedor Teste");
    expect(screen.getByLabelText("CNPJ")).toHaveValue("12.345.678/0001-90");
  });

  it("renders edit dialog with pre-filled optional fields", () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="edit"
        supplier={mockSupplier}
        onSuccess={vi.fn()}
      />,
    );

    expect(screen.getByLabelText("Endereço")).toHaveValue("Rua das Rosas, 123");
    expect(screen.getByLabelText("Cidade")).toHaveValue("São Paulo");
    expect(screen.getByLabelText("Estado (UF)")).toHaveValue("SP");
    expect(screen.getByLabelText("Website")).toHaveValue("https://buffet.com.br");
    expect(screen.getByLabelText("Observações")).toHaveValue("Fornecedor premium");
  });

  it("submits form and shows success toast on create", async () => {
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome"), "Novo Fornecedor");
    await user.type(screen.getByLabelText("E-mail"), "teste@email.com");
    await user.type(screen.getByLabelText("Telefone"), "(11) 99999-0000");
    await user.type(screen.getByLabelText("CNPJ"), "12.345.678/0001-90");
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(
      () => {
        expect(toastSuccess).toHaveBeenCalledWith(
          "Fornecedor criado com sucesso!",
        );
      },
      { timeout: 5000 },
    );
  });

  it("submits update and shows success toast on edit", async () => {
    const onSuccess = vi.fn();
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="edit"
        supplier={mockSupplier}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.clear(screen.getByLabelText("Nome"));
    await user.type(screen.getByLabelText("Nome"), "Fornecedor Editado");
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(
      () => {
        expect(toastSuccess).toHaveBeenCalledWith(
          "Fornecedor atualizado com sucesso!",
        );
      },
      { timeout: 5000 },
    );
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    const onOpenChange = vi.fn();
    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={onOpenChange}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/logistics/suppliers/", () =>
        HttpResponse.json({ detail: "CNPJ duplicado" }, { status: 409 }),
      ),
    );

    render(
      <SupplierFormDialog
        open={true}
        onOpenChange={vi.fn()}
        mode="create"
        supplier={null}
        onSuccess={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.type(screen.getByLabelText("Nome"), "Fornecedor Erro");
    await user.type(screen.getByLabelText("E-mail"), "erro@email.com");
    await user.type(screen.getByLabelText("Telefone"), "(11) 99999-0000");
    await user.type(screen.getByLabelText("CNPJ"), "12.345.678/0001-90");
    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(
      () => {
        expect(toastError).toHaveBeenCalledWith("CNPJ duplicado");
      },
      { timeout: 5000 },
    );
  });
});
