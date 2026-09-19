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
      screen.getByText(/nenhum item logístico/i),
    ).toBeInTheDocument();
  });

  it("renders item rows with colored status badge", () => {
    render(<WeddingItemsTable items={[createMockItem()]} />);

    expect(screen.getByText("Cadeiras")).toBeInTheDocument();
    expect(screen.getByText("Cadeiras Tiffany")).toBeInTheDocument();
    expect(screen.getByText("150")).toBeInTheDocument();
    expect(screen.getByText("Pendente")).toBeInTheDocument();
  });

  it("shows N/A for missing description", () => {
    render(
      <WeddingItemsTable
        items={[createMockItem({ description: "" })]}
      />,
    );

    expect(screen.getByText("N/A")).toBeInTheDocument();
  });

  it("calls onEdit when Editar is clicked in dropdown", async () => {
    const onEdit = vi.fn();
    const item = createMockItem();
    const { container } = render(<WeddingItemsTable items={[item]} onEdit={onEdit} />);

    const user = userEvent.setup();
    // Open dropdown menu using robust container selector
    await user.click(container.querySelector("button")!);

    // Find and click "Editar" item using async findByText to avoid transition flakiness
    await user.click(await screen.findByText("Editar"));

    expect(onEdit).toHaveBeenCalledWith(item);
  });

  it("opens ConfirmDeleteDialog when Excluir is clicked", async () => {
    const item = createMockItem();
    const { container } = render(<WeddingItemsTable items={[item]} onEdit={vi.fn()} />);

    const user = userEvent.setup();
    // Open dropdown
    await user.click(container.querySelector("button")!);

    // Click "Excluir" using findByText
    await user.click(await screen.findByText("Excluir"));

    // Verify dialog is open
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Excluir Item")).toBeInTheDocument();
  });

  it("successfully deletes item when confirm button is clicked", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    // Mock API success for DELETE with precise route pattern
    server.use(
      http.delete("*/api/v1/logistics/items/:uuid", () => {
        return new HttpResponse(null, { status: 204 });
      })
    );

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />
    );

    const user = userEvent.setup();
    // Open dropdown
    await user.click(container.querySelector("button")!);

    // Click "Excluir"
    await user.click(await screen.findByText("Excluir"));

    // Click "Deletar Permanentemente"
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    // Wrap assertions in waitFor to avoid async callback race conditions
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item deletado com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it("shows error toast when item deletion fails", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    // Mock API failure for DELETE with precise route pattern
    server.use(
      http.delete("*/api/v1/logistics/items/:uuid", () => {
        return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
      })
    );

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />
    );

    const user = userEvent.setup();
    // Open dropdown
    await user.click(container.querySelector("button")!);

    // Click "Excluir"
    await user.click(await screen.findByText("Excluir"));

    // Click "Deletar Permanentemente"
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    // Wrap assertions in waitFor to avoid async callback race conditions
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro interno");
      expect(onRefresh).not.toHaveBeenCalled();
    });
  });

  it("shows fallback error toast when item deletion fails without detail in body", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    // Mock API failure for DELETE returning status 500 and no body
    server.use(
      http.delete("*/api/v1/logistics/items/:uuid", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />
    );

    const user = userEvent.setup();
    // Open dropdown
    await user.click(container.querySelector("button")!);

    // Click "Excluir"
    await user.click(await screen.findByText("Excluir"));

    // Click "Deletar Permanentemente"
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    // Wrap assertions in waitFor to avoid async callback race conditions
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro ao deletar item.");
      expect(onRefresh).not.toHaveBeenCalled();
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

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
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

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Marcar como Concluído"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item concluído com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });

    // Test revert to pending
    await user.click(container.querySelector("button")!);
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

    const { container } = render(
      <WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Reabrir Aquisição"));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Item reaberto com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });
});
