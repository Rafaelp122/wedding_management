import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent } from "@/test-utils";
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
    render(<WeddingItemsTable items={[item]} onEdit={onEdit} />);

    const user = userEvent.setup();
    // Open dropdown menu
    await user.click(screen.getByRole("button"));

    // Find and click "Editar" item
    await user.click(screen.getByText("Editar"));

    expect(onEdit).toHaveBeenCalledWith(item);
  });

  it("opens ConfirmDeleteDialog when Excluir is clicked", async () => {
    const item = createMockItem();
    render(<WeddingItemsTable items={[item]} onEdit={vi.fn()} />);

    const user = userEvent.setup();
    // Open dropdown
    await user.click(screen.getByRole("button"));

    // Click "Excluir"
    await user.click(screen.getByText("Excluir"));

    // Verify dialog is open
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Excluir Item")).toBeInTheDocument();
  });

  it("successfully deletes item when confirm button is clicked", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    // Mock API success for DELETE
    server.use(
      http.delete("*/api/v1/logistics/items/*", () => {
        return new HttpResponse(null, { status: 204 });
      })
    );

    render(<WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />);

    const user = userEvent.setup();
    // Open dropdown
    await user.click(screen.getByRole("button"));

    // Click "Excluir"
    await user.click(screen.getByText("Excluir"));

    // Click "Deletar Permanentemente"
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    expect(toast.success).toHaveBeenCalledWith("Item deletado com sucesso!");
    expect(onRefresh).toHaveBeenCalled();
  });

  it("shows error toast when item deletion fails", async () => {
    const onRefresh = vi.fn();
    const item = createMockItem();

    // Mock API failure for DELETE
    server.use(
      http.delete("*/api/v1/logistics/items/*", () => {
        return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
      })
    );

    render(<WeddingItemsTable items={[item]} onEdit={vi.fn()} onRefresh={onRefresh} />);

    const user = userEvent.setup();
    // Open dropdown
    await user.click(screen.getByRole("button"));

    // Click "Excluir"
    await user.click(screen.getByText("Excluir"));

    // Click "Deletar Permanentemente"
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    expect(toast.error).toHaveBeenCalledWith("Erro interno");
    expect(onRefresh).not.toHaveBeenCalled();
  });
});
