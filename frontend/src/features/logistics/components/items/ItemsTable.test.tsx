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
});
