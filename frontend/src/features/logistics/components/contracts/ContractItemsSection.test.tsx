import { describe, expect, it } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { server } from "@/mocks/server";
import { ContractItemsSection } from "@/features/logistics/components/contracts/ContractItemsSection";
import { createMockItem } from "@/test-data";
import { toast } from "sonner";

const weddingUuid = "w-1";
const contractUuid = "c-1";

describe("ContractItemsSection", () => {
  it("shows skeleton when isLoading is true", () => {
    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={true}
      />,
    );

    expect(screen.getByText("Itens Vinculados")).toBeInTheDocument();
    expect(
      screen.queryByText("Nenhum item vinculado a este contrato."),
    ).not.toBeInTheDocument();
    expect(document.querySelector(".animate-pulse")).toBeInTheDocument();
  });

  it("shows empty message when items array is empty and not loading", () => {
    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    expect(
      screen.getByText("Nenhum item vinculado a este contrato."),
    ).toBeInTheDocument();
    expect(document.querySelector(".animate-pulse")).not.toBeInTheDocument();
  });

  it("renders items in a table", () => {
    const items = [
      createMockItem({
        uuid: "i-1",
        name: "Cadeiras",
        quantity: 150,
        acquisition_status: "PENDING",
      }),
      createMockItem({
        uuid: "i-2",
        name: "Mesas",
        quantity: 20,
        acquisition_status: "DONE",
      }),
    ];

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={items}
        isLoading={false}
      />,
    );

    expect(screen.getByText("Cadeiras")).toBeInTheDocument();
    expect(screen.getByText("Mesas")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("20")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
    expect(screen.getByText("Concluído")).toBeInTheDocument();
  });

  it("toggles inline form when 'Adicionar Item' is clicked", async () => {
    const user = userEvent.setup();

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    const addButton = screen.getByRole("button", { name: /adicionar item/i });

    expect(
      screen.queryByPlaceholderText("Nome do item"),
    ).not.toBeInTheDocument();

    await user.click(addButton);
    expect(screen.getByPlaceholderText("Nome do item")).toBeInTheDocument();

    await user.click(addButton);
    expect(
      screen.queryByPlaceholderText("Nome do item"),
    ).not.toBeInTheDocument();
  });

  it("disables save button when name is empty", async () => {
    const user = userEvent.setup();

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    await user.click(screen.getByRole("button", { name: /adicionar item/i }));

    const saveButton = screen.getByRole("button", { name: /salvar/i });
    expect(saveButton).toBeDisabled();
  });

  it("enables save button when name is filled", async () => {
    const user = userEvent.setup();

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    await user.click(screen.getByRole("button", { name: /adicionar item/i }));
    await user.type(screen.getByPlaceholderText("Nome do item"), "Novo Item");

    const saveButton = screen.getByRole("button", { name: /salvar/i });
    expect(saveButton).toBeEnabled();
  });

  it("creates item successfully and shows success toast", async () => {
    const user = userEvent.setup();

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    await user.click(screen.getByRole("button", { name: /adicionar item/i }));
    await user.type(screen.getByPlaceholderText("Nome do item"), "Novo Item");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item adicionado!");
    });

    expect(
      screen.queryByPlaceholderText("Nome do item"),
    ).not.toBeInTheDocument();
  });

  it("shows error toast on API failure", async () => {
    const { http, HttpResponse } = await import("msw");
    server.use(
      http.post("*/api/v1/logistics/items/", () =>
        HttpResponse.json({ detail: "Erro ao criar item" }, { status: 500 }),
      ),
    );

    const user = userEvent.setup();

    render(
      <ContractItemsSection
        weddingUuid={weddingUuid}
        contractUuid={contractUuid}
        items={[]}
        isLoading={false}
      />,
    );

    await user.click(screen.getByRole("button", { name: /adicionar item/i }));
    await user.type(screen.getByPlaceholderText("Nome do item"), "Novo Item");

    await user.click(screen.getByRole("button", { name: /salvar/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalled();
    }, { timeout: 5000 });
  });
});
