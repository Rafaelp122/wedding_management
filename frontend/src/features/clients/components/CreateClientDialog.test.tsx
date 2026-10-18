import { describe, expect, it, vi } from "vitest";
import { toast } from "sonner";
import { render, screen, userEvent, server, waitFor } from "@/test-utils";
import { CreateClientDialog } from "./CreateClientDialog";
import {
  getCreateClientMockHandler,
  getUpdateClientMockHandler,
} from "@/api/generated/v1/endpoints/clients/clients.msw";
import type { ClientOut } from "@/api/generated/v1/models/clientOut";

describe("CreateClientDialog", () => {
  const mockClient: ClientOut = {
    uuid: "11111111-2222-3333-4444-555555555555",
    name: "Juliana Vasconcelos",
    cpf: "123.456.789-00",
    email: "juliana@exemplo.com",
    phone: "(11) 98765-4321",
    notes: "Noiva preferencial",
    created_at: "2026-01-01T00:00:00Z",
    updated_at: "2026-01-01T00:00:00Z",
  };

  it("renders 'Novo Cliente' modal when creating", () => {
    render(
      <CreateClientDialog
        open={true}
        onOpenChange={vi.fn()}
      />,
    );

    expect(screen.getByRole("heading", { name: "Novo Cliente" })).toBeInTheDocument();
    expect(screen.getByText("Nome Completo *")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Cadastrar Cliente" })).toBeInTheDocument();
  });

  it("renders 'Editar Cliente' modal when editing with existing client data", () => {
    render(
      <CreateClientDialog
        open={true}
        onOpenChange={vi.fn()}
        client={mockClient}
      />,
    );

    expect(screen.getByRole("heading", { name: "Editar Cliente" })).toBeInTheDocument();
    expect(screen.getByDisplayValue("Juliana Vasconcelos")).toBeInTheDocument();
    expect(screen.getByDisplayValue("123.456.789-00")).toBeInTheDocument();
    expect(screen.getByDisplayValue("juliana@exemplo.com")).toBeInTheDocument();
    expect(screen.getByDisplayValue("(11) 98765-4321")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Noiva preferencial")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Salvar Alterações" })).toBeInTheDocument();
  });

  it("submits new client successfully", async () => {
    const onOpenChange = vi.fn();
    server.use(getCreateClientMockHandler(mockClient));

    render(
      <CreateClientDialog
        open={true}
        onOpenChange={onOpenChange}
      />,
    );

    const user = userEvent.setup();
    const nameInput = screen.getByPlaceholderText("Ex: Juliana Vasconcelos");
    await user.type(nameInput, "Juliana Vasconcelos");

    const submitBtn = screen.getByRole("button", { name: "Cadastrar Cliente" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Cliente cadastrado com sucesso!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });
  });

  it("submits updated client successfully", async () => {
    const onOpenChange = vi.fn();
    server.use(getUpdateClientMockHandler({ ...mockClient, name: "Juliana Silva" }));

    render(
      <CreateClientDialog
        open={true}
        onOpenChange={onOpenChange}
        client={mockClient}
      />,
    );

    const user = userEvent.setup();
    const nameInput = screen.getByPlaceholderText("Ex: Juliana Vasconcelos");
    await user.clear(nameInput);
    await user.type(nameInput, "Juliana Silva");

    const submitBtn = screen.getByRole("button", { name: "Salvar Alterações" });
    await user.click(submitBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Dados do cliente atualizados!");
      expect(onOpenChange).toHaveBeenCalledWith(false);
    });
  });
});
