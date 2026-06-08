import { describe, expect, it } from "vitest";
import { render, screen, waitFor, userEvent } from "@/test-utils";
import { StatsCards } from "@/features/dashboard/components/StatsCards";
import { createMockDashboardSummary } from "@/test-data";
import { server } from "@/mocks/server";
import { http, HttpResponse } from "msw";

describe("StatsCards", () => {
  it("renders all 4 stat cards", () => {
    render(
      <StatsCards summary={createMockDashboardSummary()} />,
    );

    expect(screen.getByText("Parcelas Vencidas")).toBeInTheDocument();
    expect(screen.getByText("Contratos Pendentes")).toBeInTheDocument();
    expect(screen.getByText(/Parcelas a Vencer/i)).toBeInTheDocument();
    expect(screen.getByText("Tarefas Atrasadas")).toBeInTheDocument();
  });

  it("shows zero values when summary is undefined", () => {
    render(<StatsCards summary={undefined} />);

    const zeros = screen.getAllByText("0");
    expect(zeros.length).toBeGreaterThanOrEqual(2);
  });

  it("renders summary values", () => {
    render(
      <StatsCards
        summary={createMockDashboardSummary({
          urgent_tasks_count: 3,
          overdue_installments_amount: "12350.00",
          overdue_installments_count: 2,
          pending_contracts_count: 5,
        })}
      />,
    );

    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 3 pendências")).toBeInTheDocument();
    expect(screen.getByText("R$ 12.350,00")).toBeInTheDocument();
    expect(screen.getByText("Ação Necessária: 2 pendências")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("Aguardando assinatura/sinal")).toBeInTheDocument();
  });

  it("opens overdue installments Sheet and renders content", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({
          items: [
            { uuid: "w1", bride_name: "Ana", groom_name: "Carlos" },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({
          items: [
            {
              uuid: "inst-1",
              installment_number: 1,
              amount: "5000.00",
              due_date: "2025-01-15",
              status: "OVERDUE",
              expense: "exp-1",
              wedding: "w1",
            },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
    );

    render(
      <StatsCards
        summary={createMockDashboardSummary({
          overdue_installments_count: 1,
          overdue_installments_amount: "5000.00",
          pending_installments_7d: "0",
        })}
      />,
    );

    const openButton = screen.getByRole("button", { name: "Ver Parcelas" });
    await user.click(openButton);

    await waitFor(() => {
      const headers = screen.getAllByText("Parcelas Vencidas");
      expect(headers.length).toBeGreaterThanOrEqual(2);
      const amounts = screen.getAllByText("R$ 5.000,00");
      expect(amounts.length).toBeGreaterThanOrEqual(1);
    });
  });

  it("opens urgent tasks Sheet and renders content", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({
          items: [
            { uuid: "w1", bride_name: "Ana", groom_name: "Carlos" },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({
          items: [
            {
              uuid: "task-1",
              title: "Contratar buffet",
              description: "Prova com fornecedor",
              is_completed: false,
              due_date: "2025-01-01",
              wedding: "w1",
            },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
    );

    render(
      <StatsCards
        summary={createMockDashboardSummary({ urgent_tasks_count: 1 })}
      />,
    );

    const taskButtons = screen.getAllByRole("button", { name: "Ver Tarefas" });
    await user.click(taskButtons[0]);

    await waitFor(() => {
      expect(screen.getByText("Contratar buffet")).toBeInTheDocument();
    });
  });

  it("opens pending contracts Sheet and renders content", async () => {
    const user = userEvent.setup();

    server.use(
      http.get("*/api/v1/weddings/", () =>
        HttpResponse.json({
          items: [
            { uuid: "w1", bride_name: "Ana", groom_name: "Carlos" },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
      http.get("*/api/v1/finances/expenses/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/finances/installments/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/scheduler/tasks/", () =>
        HttpResponse.json({ items: [], count: 0, limit: 100, offset: 0 }),
      ),
      http.get("*/api/v1/logistics/contracts/", () =>
        HttpResponse.json({
          items: [
            {
              uuid: "ctr-1",
              supplier_name: "Buffet Sabor",
              description: "Serviço completo",
              status: "DRAFT",
              total_amount: "15000.00",
              wedding: "w1",
            },
          ],
          count: 1,
          limit: 100,
          offset: 0,
        }),
      ),
    );

    render(
      <StatsCards
        summary={createMockDashboardSummary({ pending_contracts_count: 1 })}
      />,
    );

    const openButton = screen.getByRole("button", { name: "Ver Contratos" });
    await user.click(openButton);

    await waitFor(() => {
      expect(screen.getByText("Buffet Sabor")).toBeInTheDocument();
      expect(screen.getByText("R$ 15.000,00")).toBeInTheDocument();
    });
  });
});
