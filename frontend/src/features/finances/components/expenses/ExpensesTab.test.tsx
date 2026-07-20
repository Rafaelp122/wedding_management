import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent, server } from "@/test-utils";
import { http, HttpResponse } from "msw";
import { WeddingExpensesTab } from "@/features/finances/components/expenses/ExpensesTab";
import { createMockExpense } from "@/test-data";

// Pre-load ExpenseDetailSheet module into Vite registry to ensure lazy Suspense resolves synchronously in tests
import "./ExpenseDetailSheet";

const mockExpense = createMockExpense({
  uuid: "expense-1",
  name: "Banda Musical",
  description: "Banda do Casamento",
  estimated_amount: "3000.00",
  actual_amount: "3500.00",
  status: "PARTIALLY_PAID",
  paid_installments_count: 1,
  installments_count: 3,
});

describe("WeddingExpensesTab", () => {
  it("shows loading state initially", () => {
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    const skeletons = document.querySelectorAll("[class*='animate-pulse']");
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it("renders expenses card after loading", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
    );

    render(<WeddingExpensesTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(screen.getByText("Despesas Registradas")).toBeInTheDocument();
    });
    expect(screen.getByText("Banda Musical")).toBeInTheDocument();
  });

  it("shows error state when query fails", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return new HttpResponse(null, { status: 500 });
      }),
    );

    render(<WeddingExpensesTab weddingUuid="w-1" />);

    await waitFor(() => {
      expect(
        screen.getByText("Não foi possível carregar as despesas deste casamento."),
      ).toBeInTheDocument();
    });
  });

  it("opens CreateExpenseDialog when clicking Nova Despesa button", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.get("*/api/v1/finances/categories/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    // Wait for card to load
    const createBtn = await screen.findByRole("button", { name: /nova despesa/i });
    await user.click(createBtn);

    // Verify dialog opens
    expect(await screen.findByRole("heading", { name: "Nova Despesa" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Nova Despesa" })).not.toBeInTheDocument();
  });

  it("opens EditExpenseDialog when clicking Editar in action menu", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    // Click actions menu button
    const actionsBtn = await screen.findByRole("button", { name: "Ações da despesa" });
    await user.click(actionsBtn);

    // Click "Editar" menu item
    const editMenuItem = await screen.findByText("Editar");
    await user.click(editMenuItem);

    // Verify Edit dialog is open
    expect(await screen.findByRole("heading", { name: "Editar Despesa" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Editar Despesa" })).not.toBeInTheDocument();
  });

  it("opens DeleteExpenseDialog when clicking Excluir in action menu", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    // Click actions menu button
    const actionsBtn = await screen.findByRole("button", { name: "Ações da despesa" });
    await user.click(actionsBtn);

    // Click "Excluir" menu item
    const deleteMenuItem = await screen.findByText("Excluir");
    await user.click(deleteMenuItem);

    // Verify Delete dialog is open
    expect(await screen.findByRole("heading", { name: "Deletar Despesa" })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Cancelar" }));
    expect(screen.queryByRole("heading", { name: "Deletar Despesa" })).not.toBeInTheDocument();
  });

  it("opens ExpenseDetailSheet when clicking expense name", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.get("*/api/v1/finances/expenses/*", () => {
        return HttpResponse.json(mockExpense);
      }),
      http.get("*/api/v1/finances/installments*", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    // Click expense name link
    const nameLink = await screen.findByRole("button", { name: "Banda Musical" });
    await user.click(nameLink);

    // Verify details sheet is open
    expect(await screen.findByRole("heading", { name: /Banda Musical/i })).toBeInTheDocument();

    await user.click(screen.getByRole("button", { name: "Close" }));
    expect(screen.queryByRole("heading", { name: /Banda Musical/i })).not.toBeInTheDocument();
  });

  it("refreshes expenses list when EditExpenseDialog calls onSuccess", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.get("*/api/v1/logistics/contracts/", () => {
        return HttpResponse.json({ items: [], count: 0 });
      }),
      http.patch("*/api/v1/finances/expenses/*", () => {
        return HttpResponse.json(mockExpense);
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    const actionsBtn = await screen.findByRole("button", { name: "Ações da despesa" });
    await user.click(actionsBtn);

    const editMenuItem = await screen.findByText("Editar");
    await user.click(editMenuItem);

    const saveBtn = await screen.findByRole("button", { name: "Salvar Alterações" });
    await user.click(saveBtn);

    await waitFor(() => {
      expect(screen.queryByRole("heading", { name: "Editar Despesa" })).not.toBeInTheDocument();
    });
  });

  it("refreshes expenses list when DeleteExpenseDialog calls onSuccess", async () => {
    server.use(
      http.get("*/api/v1/finances/expenses/", () => {
        return HttpResponse.json({ items: [mockExpense], count: 1 });
      }),
      http.delete("*/api/v1/finances/expenses/*", () => {
        return HttpResponse.json({ success: true });
      }),
    );

    const user = userEvent.setup();
    render(<WeddingExpensesTab weddingUuid="w-1" />);

    const actionsBtn = await screen.findByRole("button", { name: "Ações da despesa" });
    await user.click(actionsBtn);

    const deleteMenuItem = await screen.findByText("Excluir");
    await user.click(deleteMenuItem);

    const confirmInput = await screen.findByPlaceholderText(/digite o nome aqui/i);
    await user.type(confirmInput, "Banda Musical");

    const confirmDeleteBtn = screen.getByRole("button", { name: /deletar permanentemente/i });
    await user.click(confirmDeleteBtn);

    await waitFor(() => {
      expect(screen.queryByRole("heading", { name: "Deletar Despesa" })).not.toBeInTheDocument();
    });
  });
});
