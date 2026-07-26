import { describe, expect, it, vi, beforeEach } from "vitest";
import { render, screen, userEvent, server, waitFor, fireEvent } from "@/test-utils";
import { CreateExpenseDialog } from "@/features/finances/components/expenses/CreateExpenseDialog";
import {
  getFinancesCategoriesListMockHandler,
  getFinancesExpensesCreateMockHandler,
} from "@/api/generated/v1/endpoints/finances/finances.msw";
import { getLogisticsContractsListMockHandler } from "@/api/generated/v1/endpoints/logistics/logistics.msw";

describe("CreateExpenseDialog", () => {
  const weddingUuid = "w-1";
  const onOpenChange = vi.fn();
  const onSuccess = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    server.use(
      getFinancesCategoriesListMockHandler({
        items: [{ uuid: "cat-1", name: "Alimentação" } as any],
        count: 1,
      }),
      getLogisticsContractsListMockHandler({
        items: [{ uuid: "con-1", name: "Contrato Buffet" } as any],
        count: 1,
      }),
      getFinancesExpensesCreateMockHandler({ uuid: "exp-1" } as any),
    );
  });

  it("renders nothing when closed", () => {
    render(
      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={false}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.queryByText("Nova Despesa")).not.toBeInTheDocument();
  });

  it("renders form fields when open", () => {
    render(
      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    expect(screen.getByText("Nova Despesa")).toBeInTheDocument();
    expect(screen.getByLabelText("Nome da Despesa")).toBeInTheDocument();
    expect(screen.getByLabelText("Categoria")).toBeInTheDocument();
    expect(screen.getByLabelText("Valor Estimado")).toBeInTheDocument();
    expect(screen.getByLabelText("Nº de Parcelas")).toBeInTheDocument();
  });

  it("shows validation error on empty submit", async () => {
    render(
      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /criar despesa/i }));

    const errors = await screen.findAllByText(/invalid/i);
    expect(errors.length).toBeGreaterThan(0);
  });

  it("calls onOpenChange when cancel is clicked", async () => {
    render(
      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /cancelar/i }));
    expect(onOpenChange).toHaveBeenCalledWith(false);
  });

  it("fills out form fields and submits successfully", async () => {
    const user = userEvent.setup();
    render(
      <CreateExpenseDialog
        weddingUuid={weddingUuid}
        open={true}
        onOpenChange={onOpenChange}
        onSuccess={onSuccess}
      />,
    );

    // Select category
    await user.click(screen.getByRole("combobox", { name: /categoria/i }));
    const categoryOption = await screen.findByRole("option", {
      name: /alimentação/i,
    });
    await user.click(categoryOption);

    // Fill name
    await user.type(screen.getByLabelText("Nome da Despesa"), "Jantar dos Noivos");

    // Fill estimated amount and actual amount
    const estimatedInput = screen.getByLabelText("Valor Estimado");
    fireEvent.change(estimatedInput, { target: { value: "3500" } });

    const actualInput = screen.getByLabelText("Valor Real (Contratado)");
    fireEvent.change(actualInput, { target: { value: "3500" } });

    // Change due date
    const dateInput = screen.getByLabelText("1º Vencimento");
    fireEvent.change(dateInput, { target: { value: "2026-11-15" } });

    // Submit
    await user.click(screen.getByRole("button", { name: /criar despesa/i }));

    await waitFor(() => {
      expect(onSuccess).toHaveBeenCalled();
    });
  });
});
