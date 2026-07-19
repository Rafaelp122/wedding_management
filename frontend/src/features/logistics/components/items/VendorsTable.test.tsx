import { describe, expect, it, vi } from "vitest";
import { render, screen, userEvent, waitFor } from "@/test-utils";
import { WeddingVendorsTable } from "@/features/logistics/components/items/VendorsTable";
import { createMockContract } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";
import { toast } from "sonner";

describe("WeddingVendorsTable", () => {
  it("shows empty state when no contracts", () => {
    render(<WeddingVendorsTable contracts={[]} />);

    expect(
      screen.getByText(/nenhum contrato de fornecedor/i),
    ).toBeInTheDocument();
  });

  it("renders contract rows with status badge and supplier name", () => {
    render(<WeddingVendorsTable contracts={[createMockContract()]} />);

    expect(screen.getByText("Assinado")).toBeInTheDocument();
    expect(screen.getByText("Buffet Gourmet Ltda")).toBeInTheDocument();
    expect(screen.getByText(/R\$\s*5\.?000/)).toBeInTheDocument();
  });

  it("shows N/A for missing signed date and description", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ signed_date: undefined, description: undefined })]}
      />,
    );

    const naValues = screen.getAllByText("N/A");
    expect(naValues.length).toBeGreaterThanOrEqual(2);
  });

  it("calls onDetail when a row is clicked", async () => {
    const onDetail = vi.fn();
    const contract = createMockContract();

    render(
      <WeddingVendorsTable
        contracts={[contract]}
        onDetail={onDetail}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByText("Assinado"));

    expect(onDetail).toHaveBeenCalledWith(contract.uuid);
  });

  it("renders addendum with indent when isAddendum returns true", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract()]}
        isAddendum={() => true}
      />,
    );

    expect(screen.getByText("↳ Aditivo")).toBeInTheDocument();
  });

  it("renders dropdown trigger when onEdit is provided", () => {
    const { container } = render(
      <WeddingVendorsTable
        contracts={[createMockContract()]}
        onEdit={vi.fn()}
      />,
    );

    const svg = container.querySelector("svg");
    expect(svg).toBeTruthy();
  });

  it("shows progress bar when contract has linked expense", () => {
    render(
      <WeddingVendorsTable
        contracts={[createMockContract({ has_linked_expense: true, progress_percent: 75 })]}
      />,
    );

    expect(screen.getByRole("progressbar")).toBeInTheDocument();
    expect(screen.getByText("75% pago")).toBeInTheDocument();
  });

  it("calls onEdit when Editar is clicked in dropdown", async () => {
    const onEdit = vi.fn();
    const contract = createMockContract();
    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={onEdit}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Editar"));

    expect(onEdit).toHaveBeenCalledWith(contract);
  });

  it("calls onGenerateExpense when Gerar Despesa is clicked in dropdown", async () => {
    const onGenerateExpense = vi.fn();
    const contract = createMockContract();
    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onGenerateExpense={onGenerateExpense}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Gerar Despesa"));

    expect(onGenerateExpense).toHaveBeenCalledWith(contract);
  });

  it("opens ConfirmDeleteDialog when Excluir is clicked in dropdown", async () => {
    const contract = createMockContract();
    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={vi.fn()}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Excluir"));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Excluir Contrato")).toBeInTheDocument();
  });

  it("successfully deletes contract when confirm button is clicked", async () => {
    const onRefresh = vi.fn();
    const contract = createMockContract();

    // Mock API success for DELETE with precise route pattern
    server.use(
      http.delete("*/api/v1/logistics/contracts/:uuid", () => {
        return new HttpResponse(null, { status: 204 });
      })
    );

    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={vi.fn()}
        onRefresh={onRefresh}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Excluir"));
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("Contrato deletado com sucesso!");
      expect(onRefresh).toHaveBeenCalled();
    });
  });

  it("shows error toast when contract deletion fails", async () => {
    const onRefresh = vi.fn();
    const contract = createMockContract();

    // Mock API failure for DELETE with precise route pattern
    server.use(
      http.delete("*/api/v1/logistics/contracts/:uuid", () => {
        return HttpResponse.json({ detail: "Erro interno" }, { status: 500 });
      })
    );

    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={vi.fn()}
        onRefresh={onRefresh}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Excluir"));
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro interno");
      expect(onRefresh).not.toHaveBeenCalled();
    });
  });

  it("shows fallback error toast when contract deletion fails without detail in body", async () => {
    const onRefresh = vi.fn();
    const contract = createMockContract();

    // Mock API failure for DELETE returning 500 and no body
    server.use(
      http.delete("*/api/v1/logistics/contracts/:uuid", () => {
        return new HttpResponse(null, { status: 500 });
      })
    );

    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={vi.fn()}
        onRefresh={onRefresh}
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);
    await user.click(await screen.findByText("Excluir"));
    await user.click(screen.getByRole("button", { name: "Deletar Permanentemente" }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Erro ao deletar contrato.");
      expect(onRefresh).not.toHaveBeenCalled();
    });
  });

  it("renders only relevant actions when some callbacks are omitted", async () => {
    const contract = createMockContract();
    const { container } = render(
      <WeddingVendorsTable
        contracts={[contract]}
        onEdit={vi.fn()}
        // onGenerateExpense is omitted
      />,
    );

    const user = userEvent.setup();
    await user.click(container.querySelector("button")!);

    expect(await screen.findByText("Editar")).toBeInTheDocument();
    expect(screen.queryByText("Gerar Despesa")).toBeNull();
  });
});
