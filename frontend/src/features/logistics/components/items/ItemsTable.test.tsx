import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { WeddingItemsTable } from "@/features/logistics/components/items/ItemsTable";
import { createMockItem } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";

describe("WeddingItemsTable", () => {
  it("shows empty state when no items", () => {
    render(<WeddingItemsTable items={[]} />);

    expect(
      screen.getByText(/nenhum item logístico planejado/i),
    ).toBeInTheDocument();
  });

  it("renders item rows with colored status badge and scope badge", () => {
    render(
      <WeddingItemsTable
        items={[
          createMockItem({
            name: "Cadeiras",
            description: "Cadeiras Tiffany",
            quantity: 150,
            scope_status: "INCLUDED",
            acquisition_status: "PENDING",
            delivery_status: "PENDING",
          }),
        ]}
      />,
    );

    expect(screen.getByText("Cadeiras")).toBeInTheDocument();
    expect(screen.getByText("Cadeiras Tiffany")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("Incluído")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
    expect(screen.getByText("Aguardando")).toBeInTheDocument();
  });

  it("shows N/A for missing description", () => {
    render(
      <WeddingItemsTable
        items={[createMockItem({ description: "" })]}
      />,
    );

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("filters items by scope tabs", async () => {
    const user = userEvent.setup();
    const items = [
      createMockItem({ uuid: "i-1", name: "Item Incluído", scope_status: "INCLUDED" }),
      createMockItem({ uuid: "i-2", name: "Item Desejado", scope_status: "DESIRED" }),
      createMockItem({
        uuid: "i-3",
        name: "Item Descartado",
        scope_status: "DISCARDED",
        rejection_reason: "Fora do orçamento",
      }),
    ];

    render(<WeddingItemsTable items={items} />);

    // Default "ALL"
    expect(screen.getByText("Item Incluído")).toBeInTheDocument();
    expect(screen.getByText("Item Desejado")).toBeInTheDocument();
    expect(screen.getByText("Item Descartado")).toBeInTheDocument();

    // Click "Desejados"
    await user.click(screen.getByRole("tab", { name: /desejados/i }));
    expect(screen.queryByText("Item Incluído")).not.toBeInTheDocument();
    expect(screen.getByText("Item Desejado")).toBeInTheDocument();
    expect(screen.queryByText("Item Descartado")).not.toBeInTheDocument();

    // Click "Descartados"
    await user.click(screen.getByRole("tab", { name: /descartados/i }));
    expect(screen.queryByText("Item Incluído")).not.toBeInTheDocument();
    expect(screen.queryByText("Item Desejado")).not.toBeInTheDocument();
    expect(screen.getByText("Item Descartado")).toBeInTheDocument();
    expect(screen.getByText(/motivo: fora do orçamento/i)).toBeInTheDocument();
  });

  it("calls onEdit when Editar is clicked in dropdown", async () => {
    const onEdit = vi.fn();
    const item = createMockItem();
    render(<WeddingItemsTable items={[item]} onEdit={onEdit} />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Editar"));

    expect(onEdit).toHaveBeenCalledWith(item);
  });

  it("opens ConfirmDeleteDialog when Excluir is clicked", async () => {
    const item = createMockItem();
    render(<WeddingItemsTable items={[item]} onEdit={vi.fn()} />);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Excluir"));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Excluir Item")).toBeInTheDocument();
  });

  it("successfully deletes item when confirm button is clicked", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    server.use(
      http.delete("*/api/v1/logistics/items/:uuid", () => {
        return new HttpResponse(null, { status: 204 });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Excluir"));
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item deletado com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it("handles discarding item with mandatory rejection reason (RF-15)", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem({ uuid: "i-discard", scope_status: "INCLUDED" });

    let capturedPayload: unknown = null;
    server.use(
      http.post("*/api/v1/logistics/items/:uuid/discard/", async ({ request }) => {
        capturedPayload = await request.json();
        return HttpResponse.json({
          ...item,
          scope_status: "DISCARDED",
          rejection_reason: (capturedPayload as { rejection_reason: string }).rejection_reason,
        });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Descartar do Escopo"));

    expect(screen.getByText("Descartar Item do Escopo")).toBeInTheDocument();
    const confirmBtn = screen.getByRole("button", { name: "Confirmar Descarte" });
    expect(confirmBtn).toBeDisabled();

    const textarea = screen.getByPlaceholderText(/fornecedor já inclui/i);
    await user.type(textarea, "Item já coberto pelo pacote do hotel");
    expect(confirmBtn).not.toBeDisabled();

    await user.click(confirmBtn);

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item descartado do escopo com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });

    expect(capturedPayload).toEqual({
      rejection_reason: "Item já coberto pelo pacote do hotel",
    });
  });

  it("handles reintegrating discarded item back into scope", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem({
      uuid: "i-reintegrate",
      scope_status: "DISCARDED",
      rejection_reason: "Custo alto",
    });

    server.use(
      http.post("*/api/v1/logistics/items/:uuid/include/", () => {
        return HttpResponse.json({ ...item, scope_status: "INCLUDED", rejection_reason: "" });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Reintegrar ao Escopo"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item reintegrado ao escopo com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it("handles delivery and return lifecycle transitions", async () => {
    const onRefresh = vi.fn();
    const itemPending = createMockItem({ uuid: "i-deliv", delivery_status: "PENDING" });

    server.use(
      http.post("*/api/v1/logistics/items/:uuid/deliver/", () => {
        return HttpResponse.json({ ...itemPending, delivery_status: "DELIVERED" });
      }),
      http.post("*/api/v1/logistics/items/:uuid/return/", () => {
        return HttpResponse.json({ ...itemPending, delivery_status: "RETURNED" });
      }),
    );

    const { rerender } = render(
      <WeddingItemsTable items={[itemPending]} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Marcar como Entregue"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item marcado como entregue!");
      expect(onRefresh).toHaveBeenCalled();
    });

    // Test return transition when item is delivered
    const itemDelivered = { ...itemPending, delivery_status: "DELIVERED" };
    rerender(<WeddingItemsTable items={[itemDelivered]} onRefresh={onRefresh} />);

    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Registrar Devolução"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item marcado como devolvido!");
    });
  });

  it("handles starting item acquisition when clicking Iniciar Aquisição", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem({ acquisition_status: "PENDING" });

    server.use(
      http.post("*/api/v1/logistics/items/:uuid/start/", () => {
        return HttpResponse.json({ ...item, acquisition_status: "IN_PROGRESS" });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Iniciar Aquisição"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Aquisição do item iniciada!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it("handles completing and reverting item when status is IN_PROGRESS", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem({ acquisition_status: "IN_PROGRESS" });

    server.use(
      http.post("*/api/v1/logistics/items/:uuid/complete/", () => {
        return HttpResponse.json({ ...item, acquisition_status: "DONE" });
      }),
      http.post("*/api/v1/logistics/items/:uuid/revert-to-pending/", () => {
        return HttpResponse.json({ ...item, acquisition_status: "PENDING" });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Marcar como Concluído"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item concluído com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });

    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Voltar para Pendente"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item retornado para pendente!");
    });
  });

  it("handles reopening item acquisition when status is DONE", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem({ acquisition_status: "DONE" });

    server.use(
      http.post("*/api/v1/logistics/items/:uuid/reopen/", () => {
        return HttpResponse.json({ ...item, acquisition_status: "IN_PROGRESS" });
      }),
    );

    render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: "Ações do item" }));
    await user.click(await screen.findByText("Reabrir Aquisição"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item reaberto com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });
});
